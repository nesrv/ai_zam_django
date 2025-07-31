from django.contrib import admin
from .models import TelegramUser, TelegramMessage, ChatMessage, ProcessedUpdate, Bot

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

@admin.register(ChatMessage)
class ChatMessageAdmin(admin.ModelAdmin):
    list_display = ['chat_id', 'from_user', 'message_text_preview', 'created_at']
    list_filter = ['chat_id', 'created_at']
    search_fields = ['message_text', 'from_user', 'chat_id']
    readonly_fields = ['created_at']
    ordering = ['-created_at']
    
    def message_text_preview(self, obj):
        return obj.message_text[:100] + "..." if len(obj.message_text) > 100 else obj.message_text
    message_text_preview.short_description = "Текст сообщения"

@admin.register(ProcessedUpdate)
class ProcessedUpdateAdmin(admin.ModelAdmin):
    list_display = ['update_id', 'processed_at']
    list_filter = ['processed_at']
    search_fields = ['update_id']
    readonly_fields = ['processed_at']
    ordering = ['-processed_at']

@admin.register(Bot)
class BotAdmin(admin.ModelAdmin):
    list_display = ['bot_name', 'user', 'is_active', 'created_at']
    list_filter = ['is_active', 'created_at', 'user']
    search_fields = ['bot_name', 'user__username']
    readonly_fields = ['created_at']
    ordering = ['-created_at']
