from django.contrib import admin
from .models import Camera

@admin.register(Camera)
class CameraAdmin(admin.ModelAdmin):
    list_display = ('name', 'url', 'objekt', 'location', 'is_active', 'created_at')
    list_filter = ('is_active', 'objekt', 'created_at')
    search_fields = ('name', 'url', 'location', 'objekt__nazvanie')
    list_editable = ('is_active',)
