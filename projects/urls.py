from django.urls import path
from . import views

app_name = 'projects'

urlpatterns = [
    path('', views.project_list_view, name='list'),
    path('upload/', views.project_upload_view, name='upload'),
    path('<int:pk>/', views.project_detail_view, name='detail'),
    path('<int:pk>/preview/', views.preview_stream_view, name='preview'),
    path('<int:pk>/download/', views.project_download_view, name='download'),
]
