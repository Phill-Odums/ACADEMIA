from django.contrib import admin
from .models import Purchase

@admin.register(Purchase)
class PurchaseAdmin(admin.ModelAdmin):
    list_display = ('paystack_reference', 'user', 'material', 'amount_paid', 'status', 'paid_at', 'created_at')
    list_filter = ('status', 'created_at')
    search_fields = ('paystack_reference', 'user__username', 'user__email', 'material__title')
    readonly_fields = ('created_at',)
