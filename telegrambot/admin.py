from django.contrib import admin
from .models import TelegramUser, TelegramMessage

@admin.register(TelegramUser)
class TelegramUserAdmin(admin.ModelAdmin):
    list_display = ['telegram_id', 'username', 'first_name', 'last_name', 'is_active', 'created_at']
    list_filter = ['is_active', 'created_at']
    search_fields = ['telegram_id', 'username', 'first_name', 'last_name']
    readonly_fields = ['created_at', 'updated_at']
    ordering = ['-created_at']

@admin.register(TelegramMessage)
class TelegramMessageAdmin(admin.ModelAdmin):
    list_display = ['user', 'message_type', 'content_preview', 'is_from_user', 'created_at']
    list_filter = ['message_type', 'is_from_user', 'created_at', 'user']
    search_fields = ['content', 'user__first_name', 'user__username']
    readonly_fields = ['created_at']
    ordering = ['-created_at']
    
    def content_preview(self, obj):
        return obj.content[:100] + "..." if len(obj.content) > 100 else obj.content
    content_preview.short_description = "Содержание"
