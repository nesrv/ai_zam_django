#!/usr/bin/env python
import os
import django

# Настройка Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ai_zam.settings')
django.setup()

from telegrambot.models import TelegramUser, TelegramMessage

def check_chat_stats():
    print("=== СТАТИСТИКА ЧАТА TELEGRAM ===")
    print(f"Всего пользователей: {TelegramUser.objects.count()}")
    print(f"Всего сообщений: {TelegramMessage.objects.count()}")
    
    print("\n=== ПОСЛЕДНИЕ 10 СООБЩЕНИЙ ===")
    messages = TelegramMessage.objects.select_related('user').order_by('-created_at')[:10]
    
    for msg in messages:
        direction = "→ Пользователь" if msg.is_from_user else "← Бот"
        print(f"{msg.created_at.strftime('%H:%M:%S')} | {msg.user.first_name} | {direction} | {msg.content[:60]}...")
    
    print("\n=== СТАТИСТИКА ПО ТИПАМ ===")
    from django.db.models import Count
    message_types = TelegramMessage.objects.values('message_type').annotate(count=Count('id'))
    for mt in message_types:
        print(f"{mt['message_type']}: {mt['count']}")
    
    print("\n=== АКТИВНЫЕ ПОЛЬЗОВАТЕЛИ ===")
    active_users = TelegramUser.objects.filter(is_active=True)
    for user in active_users:
        msg_count = user.messages.count()
        print(f"{user.first_name} (@{user.username}): {msg_count} сообщений")

if __name__ == "__main__":
    check_chat_stats() 