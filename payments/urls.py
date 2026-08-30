from django.urls import path
from . import views

app_name = 'payments'

urlpatterns = [
    path('initiate/<int:material_id>/', views.initialize_purchase_view, name='initiate'),
    path('callback/', views.payment_callback_view, name='callback'),
    path('webhook/', views.paystack_webhook_view, name='webhook'),
    path('receipt/<str:reference>/', views.payment_receipt_view, name='receipt'),
    path('library/', views.buyer_library_view, name='library'),
]
