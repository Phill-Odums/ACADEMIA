from django.shortcuts import render
from projects.models import ProjectMaterial
from departments.models import Department
from analytics.models import DownloadLog
from django.db.models import Count, Q

def home_view(request):
    featured_materials = ProjectMaterial.objects.filter(
        status=ProjectMaterial.Status.APPROVED
    ).select_related('department', 'uploaded_by').order_by('-created_at')[:6]

    departments = Department.objects.annotate(
        mat_count=Count('materials', filter=Q(materials__status=ProjectMaterial.Status.APPROVED))
    ).order_by('-mat_count')[:6]

    total_projects = ProjectMaterial.objects.filter(status=ProjectMaterial.Status.APPROVED).count()
    total_departments = Department.objects.count()
    total_downloads = DownloadLog.objects.count()

    context = {
        'featured_materials': featured_materials,
        'departments': departments,
        'total_projects': total_projects,
        'total_departments': total_departments,
        'total_downloads': total_downloads,
    }
    return render(request, 'home.html', context)
