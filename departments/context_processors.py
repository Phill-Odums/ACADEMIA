from .models import Department

def department_list(request):
    try:
        departments = Department.objects.all()
    except Exception:
        departments = []
    return {'all_departments': departments}
