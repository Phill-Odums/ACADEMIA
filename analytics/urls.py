from django.urls import path
from . import views

app_name = 'analytics'

urlpatterns = [
    path('staff/', views.staff_dashboard_view, name='staff_dashboard'),
    path('admin-hub/', views.superadmin_dashboard_view, name='admin_dashboard'),
    path('approve/<int:pk>/', views.approve_material_view, name='approve_material'),
    path('reject/<int:pk>/', views.reject_material_view, name='reject_material'),
    path('interest/<int:pk>/', views.capture_interest_view, name='capture_interest'),
]
