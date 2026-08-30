import json
import uuid
from django.shortcuts import render, get_object_or_404, redirect
from django.http import HttpResponse, JsonResponse, HttpResponseBadRequest
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
from django.urls import reverse

from .models import Purchase
from .paystack import initialize_paystack_payment, verify_paystack_payment, verify_paystack_webhook_signature
from projects.models import ProjectMaterial

@login_required
def initialize_purchase_view(request, material_id):
    material = get_object_or_404(ProjectMaterial, pk=material_id, status=ProjectMaterial.Status.APPROVED)

    # Check if user already owns this material
    existing = Purchase.objects.filter(user=request.user, material=material, status=Purchase.Status.SUCCESS).first()
    if existing:
        messages.info(request, "You already have access to this academic project.")
        return redirect('projects:detail', pk=material.pk)

    # Generate unique transaction reference
    reference = f"APM_{uuid.uuid4().hex[:12].upper()}"

    # Create pending Purchase record
    purchase = Purchase.objects.create(
        material=material,
        user=request.user,
        customer_email=request.user.email or f"{request.user.username}@marketplace.local",
        paystack_reference=reference,
        amount_paid=material.price,
        status=Purchase.Status.PENDING
    )

    callback_url = request.build_absolute_uri(reverse('payments:callback'))
    
    init_res = initialize_paystack_payment(
        email=purchase.customer_email,
        amount_in_naira=material.price,
        reference=reference,
        callback_url=callback_url,
        metadata={
            'material_id': material.id,
            'user_id': request.user.id,
            'material_title': material.title,
        }
    )

    if init_res.get('status') and 'data' in init_res and 'authorization_url' in init_res['data']:
        auth_url = init_res['data']['authorization_url']
        return redirect(auth_url)
    else:
        purchase.status = Purchase.Status.FAILED
        purchase.save()
        messages.error(request, f"Unable to initialize payment: {init_res.get('message', 'Please try again later.')}")
        return redirect('projects:detail', pk=material.pk)

def payment_callback_view(request):
    reference = request.GET.get('reference') or request.GET.get('trxref')
    if not reference:
        messages.error(request, "No transaction reference received.")
        return redirect('home')

    purchase = Purchase.objects.filter(paystack_reference=reference).select_related('material', 'user').first()
    if not purchase:
        messages.error(request, f"Transaction record for {reference} was not found.")
        return redirect('home')

    # If already SUCCESS
    if purchase.status == Purchase.Status.SUCCESS:
        return render(request, 'payments/success.html', {'purchase': purchase})

    # Verify transaction with Paystack
    verify_res = verify_paystack_payment(reference)

    if verify_res.get('status') and verify_res.get('data', {}).get('status') == 'success':
        purchase.status = Purchase.Status.SUCCESS
        purchase.paid_at = timezone.now()
        purchase.save()
        messages.success(request, f"Payment successful! You now have full access to '{purchase.material.title}'.")
        return render(request, 'payments/success.html', {'purchase': purchase})
    else:
        purchase.status = Purchase.Status.FAILED
        purchase.save()
        messages.error(request, "Payment verification failed or payment was cancelled.")
        return render(request, 'payments/failed.html', {'purchase': purchase})

@csrf_exempt
def paystack_webhook_view(request):
    if request.method != 'POST':
        return HttpResponse(status=405)

    signature = request.META.get('HTTP_X_PAYSTACK_SIGNATURE', '')
    if not verify_paystack_webhook_signature(request.body, signature):
        return HttpResponseBadRequest("Invalid signature")

    try:
        payload = json.loads(request.body.decode('utf-8'))
    except Exception:
        return HttpResponseBadRequest("Invalid JSON")

    event = payload.get('event')
    data = payload.get('data', {})

    if event == 'charge.success':
        reference = data.get('reference')
        if reference:
            purchase = Purchase.objects.filter(paystack_reference=reference).first()
            if purchase and purchase.status != Purchase.Status.SUCCESS:
                purchase.status = Purchase.Status.SUCCESS
                purchase.paid_at = timezone.now()
                purchase.save()

    return HttpResponse(status=200)

@login_required
def buyer_library_view(request):
    purchases = Purchase.objects.filter(
        user=request.user,
        status=Purchase.Status.SUCCESS
    ).select_related('material', 'material__department').order_by('-paid_at')

    return render(request, 'buyer/library.html', {'purchases': purchases})

@login_required
def payment_receipt_view(request, reference):
    purchase = get_object_or_404(Purchase, paystack_reference=reference)
    if not (request.user.is_superadmin_user() or purchase.user == request.user):
        messages.error(request, "Unauthorized access to receipt.")
        return redirect('home')

    return render(request, 'payments/receipt.html', {'purchase': purchase})
