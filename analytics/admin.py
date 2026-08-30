from django.contrib import admin
from .models import Interest, DownloadLog

@admin.register(Interest)
class InterestAdmin(admin.ModelAdmin):
    list_display = ('material', 'user', 'email', 'created_at')
    list_filter = ('created_at',)
    search_fields = ('material__title', 'user__username', 'email')

@admin.register(DownloadLog)
class DownloadLogAdmin(admin.ModelAdmin):
    list_display = ('material', 'user', 'downloaded_at')
    list_filter = ('downloaded_at',)
    search_fields = ('material__title', 'user__username')
