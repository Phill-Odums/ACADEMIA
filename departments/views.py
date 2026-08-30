from django.shortcuts import render, get_object_or_404
from .models import Department
from projects.models import ProjectMaterial

def department_list_view(request):
    departments = Department.objects.all()
    return render(request, 'departments/list.html', {'departments': departments})

def department_detail_view(request, slug):
    department = get_object_or_404(Department, slug=slug)
    materials = ProjectMaterial.objects.filter(department=department, status=ProjectMaterial.Status.APPROVED).order_by('-created_at')
    return render(request, 'departments/detail.html', {
        'department': department,
        'materials': materials,
    })
