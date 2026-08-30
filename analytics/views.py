from django.shortcuts import render, get_object_or_404, redirect
from django.http import JsonResponse, HttpResponseForbidden
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST
from django.contrib import messages
from django.db.models import Sum, Count, Q

from projects.models import ProjectMaterial
from payments.models import Purchase
from departments.models import Department
from .models import Interest, DownloadLog

@login_required
def staff_dashboard_view(request):
    if not request.user.is_staff_user():
        messages.error(request, "Staff access required.")
        return redirect('home')

    materials = ProjectMaterial.objects.filter(uploaded_by=request.user).select_related('department').order_by('-created_at')

    # Aggregations for staff uploads
    total_materials = materials.count()
    approved_count = materials.filter(status=ProjectMaterial.Status.APPROVED).count()
    pending_count = materials.filter(status=ProjectMaterial.Status.PENDING).count()
    rejected_count = materials.filter(status=ProjectMaterial.Status.REJECTED).count()

    total_interests = Interest.objects.filter(material__uploaded_by=request.user).count()
    total_purchases = Purchase.objects.filter(material__uploaded_by=request.user, status=Purchase.Status.SUCCESS).count()
    total_downloads = DownloadLog.objects.filter(material__uploaded_by=request.user).count()

    total_revenue_res = Purchase.objects.filter(
        material__uploaded_by=request.user,
        status=Purchase.Status.SUCCESS
    ).aggregate(total=Sum('amount_paid'))
    total_revenue = total_revenue_res['total'] or 0

    recent_interests = Interest.objects.filter(material__uploaded_by=request.user).select_related('material', 'user').order_by('-created_at')[:8]
    recent_purchases = Purchase.objects.filter(material__uploaded_by=request.user, status=Purchase.Status.SUCCESS).select_related('material', 'user').order_by('-created_at')[:8]

    context = {
        'materials': materials,
        'total_materials': total_materials,
        'approved_count': approved_count,
        'pending_count': pending_count,
        'rejected_count': rejected_count,
        'total_interests': total_interests,
        'total_purchases': total_purchases,
        'total_downloads': total_downloads,
        'total_revenue': total_revenue,
        'recent_interests': recent_interests,
        'recent_purchases': recent_purchases,
    }
    return render(request, 'dashboard/staff_dashboard.html', context)

@login_required
def superadmin_dashboard_view(request):
    if not request.user.is_superadmin_user():
        messages.error(request, "Super Administrator access required.")
        return redirect('home')

    # Review queue (pending uploads)
    pending_materials = ProjectMaterial.objects.filter(status=ProjectMaterial.Status.PENDING).select_related('department', 'uploaded_by').order_by('-created_at')
    
    # All materials
    all_materials = ProjectMaterial.objects.all().select_related('department', 'uploaded_by').order_by('-created_at')

    total_projects = all_materials.count()
    approved_count = all_materials.filter(status=ProjectMaterial.Status.APPROVED).count()
    pending_count = pending_materials.count()

    total_revenue_res = Purchase.objects.filter(status=Purchase.Status.SUCCESS).aggregate(total=Sum('amount_paid'))
    total_revenue = total_revenue_res['total'] or 0

    total_purchases = Purchase.objects.filter(status=Purchase.Status.SUCCESS).count()
    total_interests = Interest.objects.count()
    total_downloads = DownloadLog.objects.count()

    departments = Department.objects.annotate(
        mat_count=Count('materials', filter=Q(materials__status=ProjectMaterial.Status.APPROVED))
    ).order_by('-mat_count')

    recent_purchases = Purchase.objects.filter(status=Purchase.Status.SUCCESS).select_related('material', 'user').order_by('-created_at')[:10]
    recent_leads = Interest.objects.select_related('material', 'user').order_by('-created_at')[:10]

    context = {
        'pending_materials': pending_materials,
        'all_materials': all_materials,
        'total_projects': total_projects,
        'approved_count': approved_count,
        'pending_count': pending_count,
        'total_revenue': total_revenue,
        'total_purchases': total_purchases,
        'total_interests': total_interests,
        'total_downloads': total_downloads,
        'departments': departments,
        'recent_purchases': recent_purchases,
        'recent_leads': recent_leads,
    }
    return render(request, 'dashboard/admin_dashboard.html', context)

@login_required
@require_POST
def approve_material_view(request, pk):
    if not request.user.is_superadmin_user():
        return HttpResponseForbidden("Only super admins can approve projects.")
    
    material = get_object_or_404(ProjectMaterial, pk=pk)
    material.status = ProjectMaterial.Status.APPROVED
    material.rejection_reason = ""
    material.save()
    messages.success(request, f"Project '{material.title}' has been approved and published to the marketplace.")
    return redirect('analytics:admin_dashboard')

@login_required
@require_POST
def reject_material_view(request, pk):
    if not request.user.is_superadmin_user():
        return HttpResponseForbidden("Only super admins can reject projects.")

    material = get_object_or_404(ProjectMaterial, pk=pk)
    reason = request.POST.get('rejection_reason', 'Does not meet departmental quality standards.')
    material.status = ProjectMaterial.Status.REJECTED
    material.rejection_reason = reason
    material.save()
    messages.warning(request, f"Project '{material.title}' has been rejected.")
    return redirect('analytics:admin_dashboard')

@require_POST
def capture_interest_view(request, pk):
    material = get_object_or_404(ProjectMaterial, pk=pk)
    email = request.POST.get('email', '').strip()
    note = request.POST.get('note', '').strip()
    user = request.user if request.user.is_authenticated else None

    if not user and not email:
        return JsonResponse({'status': 'error', 'message': 'Please provide your email.'}, status=400)

    Interest.objects.create(
        material=material,
        user=user,
        email=email,
        note=note
    )
    return JsonResponse({
        'status': 'success',
        'message': "Thank you! Your interest has been recorded. Our department coordinator will reach out."
    })
