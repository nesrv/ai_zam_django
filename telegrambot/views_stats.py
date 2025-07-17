import logging
from django.shortcuts import render
from django.http import JsonResponse
from django.db.models import Count
from django.utils import timezone
from datetime import timedelta
from .models import TelegramUser, TelegramMessage, ChatMessage

logger = logging.getLogger(__name__)

def messages_stats(request):
    """Страница со статистикой сообщений"""
    try:
        # Общая статистика
        chat_messages_count = ChatMessage.objects.count()
        telegram_messages_count = TelegramMessage.objects.count()
        users_count = TelegramUser.objects.count()
        chats_count = ChatMessage.objects.values('chat_id').distinct().count()
        
        # Статистика за последние 24 часа и неделю
        day_ago = timezone.now() - timedelta(days=1)
        week_ago = timezone.now() - timedelta(days=7)
        
        messages_today = (
            ChatMessage.objects.filter(created_at__gte=day_ago).count() +
            TelegramMessage.objects.filter(created_at__gte=day_ago).count()
        )
        
        messages_week = (
            ChatMessage.objects.filter(created_at__gte=week_ago).count() +
            TelegramMessage.objects.filter(created_at__gte=week_ago).count()
        )
        
        new_users_week = TelegramUser.objects.filter(created_at__gte=week_ago).count()
        
        # Последние сообщения
        recent_chat_messages = ChatMessage.objects.order_by('-created_at')[:10]
        recent_telegram_messages = TelegramMessage.objects.select_related('user').order_by('-created_at')[:10]
        
        context = {
            'chat_messages_count': chat_messages_count,
            'telegram_messages_count': telegram_messages_count,
            'users_count': users_count,
            'chats_count': chats_count,
            'messages_today': messages_today,
            'messages_week': messages_week,
            'new_users_week': new_users_week,
            'recent_chat_messages': recent_chat_messages,
            'recent_telegram_messages': recent_telegram_messages
        }
        
        return render(request, 'telegrambot/messages_stats.html', context)
        
    except Exception as e:
        logger.error(f"Ошибка получения статистики сообщений: {e}")
        return JsonResponse({'error': str(e)}, status=500)