import os
import mimetypes
from django.shortcuts import render, get_object_or_404, redirect
from django.http import HttpResponse, Http404, FileResponse, JsonResponse
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.paginator import Paginator
from django.db.models import Q, Count
from django.conf import settings

from .models import ProjectMaterial
from .forms import ProjectMaterialUploadForm
from .services import generate_preview_pdf
from departments.models import Department
from payments.models import Purchase
from analytics.models import DownloadLog, Interest

def project_list_view(request):
    materials = ProjectMaterial.objects.filter(status=ProjectMaterial.Status.APPROVED).select_related('department', 'uploaded_by')

    # Search query
    query = request.GET.get('q', '').strip()
    if query:
        materials = materials.filter(
            Q(title__icontains=query) |
            Q(abstract__icontains=query) |
            Q(keywords__icontains=query) |
            Q(department__name__icontains=query)
        )

    # Department filter
    dept_slug = request.GET.get('department', '').strip()
    selected_dept = None
    if dept_slug:
        selected_dept = Department.objects.filter(slug=dept_slug).first()
        if selected_dept:
            materials = materials.filter(department=selected_dept)

    # Tag / Keyword filter
    tag = request.GET.get('tag', '').strip()
    if tag:
        materials = materials.filter(keywords__icontains=tag)

    # Price range filter
    min_price = request.GET.get('min_price', '').strip()
    max_price = request.GET.get('max_price', '').strip()
    if min_price:
        try:
            materials = materials.filter(price__gte=float(min_price))
        except ValueError:
            pass
    if max_price:
        try:
            materials = materials.filter(price__lte=float(max_price))
        except ValueError:
            pass

    # Sorting
    sort = request.GET.get('sort', 'newest')
    if sort == 'price_low':
        materials = materials.order_by('price')
    elif sort == 'price_high':
        materials = materials.order_by('-price')
    elif sort == 'oldest':
        materials = materials.order_by('created_at')
    elif sort == 'popular':
        materials = materials.annotate(num_purchases=Count('purchases')).order_by('-num_purchases', '-created_at')
    else:
        materials = materials.order_by('-created_at')

    # Pagination
    paginator = Paginator(materials, 9)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    departments = Department.objects.all()

    context = {
        'page_obj': page_obj,
        'departments': departments,
        'selected_dept': selected_dept,
        'query': query,
        'tag': tag,
        'sort': sort,
        'min_price': min_price,
        'max_price': max_price,
        'total_count': paginator.count,
    }
    return render(request, 'projects/list.html', context)

def project_detail_view(request, pk):
    material = get_object_or_404(ProjectMaterial, pk=pk)
    
    # Check if user has purchased this material or is owner/admin
    has_purchased = False
    if request.user.is_authenticated:
        if request.user.is_superadmin_user() or material.uploaded_by == request.user:
            has_purchased = True
        else:
            has_purchased = Purchase.objects.filter(
                user=request.user,
                material=material,
                status=Purchase.Status.SUCCESS
            ).exists()

    # Log an interest event on preview visit
    if not has_purchased:
        user_param = request.user if request.user.is_authenticated else None
        Interest.objects.create(material=material, user=user_param)

    related_materials = ProjectMaterial.objects.filter(
        department=material.department,
        status=ProjectMaterial.Status.APPROVED
    ).exclude(pk=material.pk)[:3]

    context = {
        'material': material,
        'has_purchased': has_purchased,
        'related_materials': related_materials,
    }
    return render(request, 'projects/detail.html', context)

def preview_stream_view(request, pk):
    """
    Streams the 2-page preview inline.
    """
    material = get_object_or_404(ProjectMaterial, pk=pk)
    
    # If preview file doesn't exist yet, try generating it
    if not material.preview_file or not os.path.exists(material.preview_file.path):
        generated = generate_preview_pdf(material)
        if generated:
            material.save()

    if material.preview_file and os.path.exists(material.preview_file.path):
        response = FileResponse(open(material.preview_file.path, 'rb'), content_type='application/pdf')
        response['Content-Disposition'] = f'inline; filename="preview_{material.id}.pdf"'
        return response
    
    raise Http404("Preview not available for this project material.")

@login_required
def project_download_view(request, pk):
    """
    Protected full document download view.
    Ensures that only buyers with a SUCCESS purchase status, author, or superadmins can download.
    """
    material = get_object_or_404(ProjectMaterial, pk=pk)

    # Permission check
    can_download = False
    if request.user.is_superadmin_user() or material.uploaded_by == request.user:
        can_download = True
    else:
        can_download = Purchase.objects.filter(
            user=request.user,
            material=material,
            status=Purchase.Status.SUCCESS
        ).exists()

    if not can_download:
        messages.error(request, "You must purchase this academic material to download the full document.")
        return redirect('projects:detail', pk=material.pk)

    if not material.file or not os.path.exists(material.file.path):
        raise Http404("The full project file was not found on the server.")

    # Record download log
    DownloadLog.objects.create(material=material, user=request.user)

    file_path = material.file.path
    content_type, _ = mimetypes.guess_type(file_path)
    if not content_type:
        content_type = 'application/octet-stream'

    filename = os.path.basename(file_path)
    response = FileResponse(open(file_path, 'rb'), content_type=content_type)
    response['Content-Disposition'] = f'attachment; filename="{filename}"'
    return response

@login_required
def project_upload_view(request):
    if not request.user.is_staff_user():
        messages.error(request, "Access restricted to department staff and super administrators.")
        return redirect('home')

    if request.method == 'POST':
        form = ProjectMaterialUploadForm(request.POST, request.FILES, user=request.user)
        if form.is_valid():
            material = form.save(commit=False)
            material.uploaded_by = request.user
            material.save()

            # Generate 2-page preview immediately
            preview_created = generate_preview_pdf(material)
            if preview_created:
                material.save()

            if material.status == ProjectMaterial.Status.APPROVED:
                messages.success(request, f"Project '{material.title}' uploaded and automatically approved!")
                return redirect('projects:detail', pk=material.pk)
            else:
                messages.success(request, f"Project '{material.title}' submitted successfully and is awaiting Super Admin approval.")
                return redirect('analytics:staff_dashboard')
        else:
            messages.error(request, "Please fix the errors below to submit the project.")
    else:
        form = ProjectMaterialUploadForm(user=request.user)

    return render(request, 'projects/upload.html', {'form': form})
