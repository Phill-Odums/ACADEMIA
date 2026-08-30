from django.contrib import admin
from .models import ProjectMaterial

@admin.register(ProjectMaterial)
class ProjectMaterialAdmin(admin.ModelAdmin):
    list_display = ("title", "department", "uploaded_by", "status", "price", "created_at")
    list_filter = ("status", "department")
    search_fields = ("title", "abstract", "keywords")
    readonly_fields = ("created_at", "updated_at")

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        if request.user.is_superuser or (hasattr(request.user, 'role') and request.user.role == 'SUPERADMIN'):
            return qs
        return qs.filter(uploaded_by=request.user)

    def save_model(self, request, obj, form, change):
        if not change and not obj.uploaded_by_id:
            obj.uploaded_by = request.user
        super().save_model(request, obj, form, change)
