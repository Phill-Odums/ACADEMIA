from django.urls import path
from . import views

app_name = 'departments'

urlpatterns = [
    path('', views.department_list_view, name='list'),
    path('<slug:slug>/', views.department_detail_view, name='detail'),
]
