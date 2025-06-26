from django.contrib import admin
from .models import AIModel, ChatSession, ChatMessage

@admin.register(AIModel)
class AIModelAdmin(admin.ModelAdmin):
    list_display = ['name', 'created_at', 'is_active']
    list_filter = ['is_active', 'created_at']
    search_fields = ['name', 'description']
    readonly_fields = ['created_at']

@admin.register(ChatSession)
class ChatSessionAdmin(admin.ModelAdmin):
    list_display = ['session_id', 'user', 'created_at', 'updated_at', 'is_active']
    list_filter = ['is_active', 'created_at', 'updated_at']
    search_fields = ['session_id', 'user__username']
    readonly_fields = ['created_at', 'updated_at']

@admin.register(ChatMessage)
class ChatMessageAdmin(admin.ModelAdmin):
    list_display = ['session', 'message_type', 'content_preview', 'created_at']
    list_filter = ['message_type', 'created_at', 'session']
    search_fields = ['content', 'session__session_id']
    readonly_fields = ['created_at']
    
    def content_preview(self, obj):
        return obj.content[:100] + "..." if len(obj.content) > 100 else obj.content
    content_preview.short_description = "Содержание"
