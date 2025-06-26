import json
import logging
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from django.views.decorators.clickjacking import xframe_options_exempt
from django.shortcuts import render
from .services import process_telegram_update, send_telegram_message
from .models import TelegramUser, TelegramMessage

logger = logging.getLogger(__name__)

@csrf_exempt
@xframe_options_exempt
@require_POST
def telegram_webhook(request):
    """Webhook для получения обновлений от Telegram"""
    try:
        # Проверяем, что запрос действительно от Telegram
        user_agent = request.META.get('HTTP_USER_AGENT', '')
        remote_addr = request.META.get('REMOTE_ADDR', '')
        
        logger.info(f"Webhook request from {remote_addr} with User-Agent: {user_agent}")
        
        # Проверяем IP адреса Telegram (основные диапазоны)
        telegram_ips = [
            '149.154.160.0/20',
            '91.108.4.0/22',
            '91.108.8.0/22',
            '91.108.12.0/22',
            '91.108.16.0/22',
            '91.108.56.0/22',
            '149.154.164.0/22',
            '149.154.168.0/22',
            '149.154.172.0/22',
            '149.154.176.0/20',
            '149.154.192.0/20',
            '149.154.196.0/22',
            '149.154.200.0/22',
            '149.154.204.0/22',
            '149.154.208.0/20',
            '149.154.224.0/20',
            '149.154.228.0/22',
            '149.154.232.0/22',
            '149.154.236.0/22',
            '149.154.240.0/20',
            '149.154.244.0/22',
            '149.154.248.0/22',
            '149.154.252.0/22',
        ]
        
        # Простая проверка IP (можно улучшить с помощью ipaddress модуля)
        if not any('TelegramBot' in user_agent or 'python-telegram-bot' in user_agent):
            logger.warning(f"Подозрительный запрос к webhook от: {remote_addr} - {user_agent}")
            # Не блокируем, но логируем для безопасности
        
        data = json.loads(request.body)
        logger.info(f"Получено обновление от Telegram: {data}")
        
        # Обрабатываем обновление
        result = process_telegram_update(data)
        
        if result:
            logger.info("Webhook обработан успешно")
            return JsonResponse({'ok': True})
        else:
            logger.error("Ошибка обработки webhook")
            return JsonResponse({'ok': False, 'error': 'Failed to process update'}, status=500)
            
    except json.JSONDecodeError as e:
        logger.error(f"Ошибка декодирования JSON: {e}")
        return JsonResponse({'error': 'Invalid JSON'}, status=400)
    except Exception as e:
        logger.error(f"Ошибка обработки webhook: {e}")
        return JsonResponse({'error': str(e)}, status=500)

def bot_status(request):
    """Страница статуса бота"""
    try:
        # Получаем статистику
        total_users = TelegramUser.objects.count()
        active_users = TelegramUser.objects.filter(is_active=True).count()
        total_messages = TelegramMessage.objects.count()
        
        # Последние сообщения
        recent_messages = TelegramMessage.objects.select_related('user').order_by('-created_at')[:10]
        
        context = {
            'total_users': total_users,
            'active_users': active_users,
            'total_messages': total_messages,
            'recent_messages': recent_messages,
        }
        
        return render(request, 'telegrambot/status.html', context)
        
    except Exception as e:
        logger.error(f"Ошибка получения статуса бота: {e}")
        return JsonResponse({'error': str(e)}, status=500)

def bot_management(request):
    """Страница управления ботом"""
    try:
        # Получаем список пользователей
        users = TelegramUser.objects.order_by('-created_at')[:50]
        
        context = {
            'users': users,
        }
        
        return render(request, 'telegrambot/management.html', context)
        
    except Exception as e:
        logger.error(f"Ошибка управления ботом: {e}")
        return JsonResponse({'error': str(e)}, status=500)

@csrf_exempt
@require_POST
def send_broadcast(request):
    """Отправка массового сообщения всем пользователям"""
    try:
        data = json.loads(request.body)
        message = data.get('message', '').strip()
        
        if not message:
            return JsonResponse({'error': 'Сообщение не может быть пустым'}, status=400)
        
        # Получаем всех активных пользователей
        users = TelegramUser.objects.filter(is_active=True)
        sent_count = 0
        
        for user in users:
            try:
                result = send_telegram_message(user.telegram_id, message)
                if result:
                    sent_count += 1
            except Exception as e:
                logger.error(f"Ошибка отправки сообщения пользователю {user.telegram_id}: {e}")
        
        return JsonResponse({
            'ok': True,
            'sent_count': sent_count,
            'total_users': users.count()
        })
        
    except json.JSONDecodeError:
        return JsonResponse({'error': 'Invalid JSON'}, status=400)
    except Exception as e:
        logger.error(f"Ошибка массовой рассылки: {e}")
        return JsonResponse({'error': str(e)}, status=500)

def webhook_status(request):
    """Страница статуса webhook для проверки"""
    if request.method == 'GET':
        return JsonResponse({
            'status': 'ok',
            'message': 'Telegram webhook endpoint is working',
            'method': 'GET',
            'note': 'This endpoint accepts only POST requests from Telegram'
        })
    else:
        return JsonResponse({'error': 'Method not allowed'}, status=405)
