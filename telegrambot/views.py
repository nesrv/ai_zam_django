import json
import logging
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from django.views.decorators.clickjacking import xframe_options_exempt
from django.shortcuts import render
from django.db.models import Count, Q
from django.utils import timezone
from datetime import timedelta
from .services import process_telegram_update, send_telegram_message, check_bot_token, BOT_TOKEN
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
    """Страница статуса бота с чатом"""
    try:
        # Получаем статистику
        total_users = TelegramUser.objects.count()
        active_users = TelegramUser.objects.filter(is_active=True).count()
        total_messages = TelegramMessage.objects.count()
        
        # Получаем все сообщения для чата, отсортированные по времени
        all_messages = TelegramMessage.objects.select_related('user').order_by('created_at')
        
        # Последние сообщения для статистики (первые 10)
        recent_messages = all_messages[:10]
        
        context = {
            'total_users': total_users,
            'active_users': active_users,
            'total_messages': total_messages,
            'recent_messages': recent_messages,
            'all_messages': all_messages,  # Все сообщения для чата
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
        total_users = users.count()
        
        if total_users == 0:
            return JsonResponse({
                'ok': False,
                'error': 'Нет активных пользователей для отправки сообщения',
                'sent_count': 0,
                'total_users': 0
            })
        
        # Проверяем токен бота перед отправкой
        token = BOT_TOKEN
        is_valid, bot_info = check_bot_token(token)
        if not is_valid:
            return JsonResponse({
                'ok': False,
                'error': f'Недействительный токен бота: {bot_info}',
                'sent_count': 0,
                'total_users': total_users
            })
        
        sent_count = 0
        failed_count = 0
        errors = []
        
        for user in users:
            try:
                logger.info(f"Отправка сообщения пользователю {user.telegram_id} ({user.first_name})")
                result = send_telegram_message(user.telegram_id, message)
                
                if result and result.get('ok'):
                    sent_count += 1
                    logger.info(f"✅ Сообщение успешно отправлено пользователю {user.telegram_id}")
                else:
                    failed_count += 1
                    error_msg = f"Ошибка отправки пользователю {user.telegram_id}: {result}"
                    errors.append(error_msg)
                    logger.error(error_msg)
                    
                    # Если пользователь заблокировал бота, помечаем его как неактивного
                    if result and result.get('error_code') == 400:
                        description = result.get('description', '').lower()
                        if 'bot was blocked' in description or 'chat not found' in description:
                            user.is_active = False
                            user.save()
                            logger.info(f"Пользователь {user.telegram_id} помечен как неактивный")
                    
            except Exception as e:
                failed_count += 1
                error_msg = f"Исключение при отправке пользователю {user.telegram_id}: {str(e)}"
                errors.append(error_msg)
                logger.error(error_msg)
        
        logger.info(f"Массовая рассылка завершена: {sent_count}/{total_users} успешно отправлено")
        
        return JsonResponse({
            'ok': True,
            'sent_count': sent_count,
            'failed_count': failed_count,
            'total_users': total_users,
            'errors': errors[:5] if errors else []  # Возвращаем только первые 5 ошибок
        })
        
    except json.JSONDecodeError:
        return JsonResponse({'error': 'Invalid JSON'}, status=400)
    except Exception as e:
        logger.error(f"Общая ошибка массовой рассылки: {e}")
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

def bot_dashboard(request):
    """Главная страница с историей и активностью бота"""
    try:
        # Общая статистика
        total_users = TelegramUser.objects.count()
        active_users = TelegramUser.objects.filter(is_active=True).count()
        total_messages = TelegramMessage.objects.count()
        
        # Статистика за последние 7 дней
        week_ago = timezone.now() - timedelta(days=7)
        new_users_week = TelegramUser.objects.filter(created_at__gte=week_ago).count()
        messages_week = TelegramMessage.objects.filter(created_at__gte=week_ago).count()
        
        # Статистика за последние 24 часа
        day_ago = timezone.now() - timedelta(days=1)
        new_users_day = TelegramUser.objects.filter(created_at__gte=day_ago).count()
        messages_day = TelegramMessage.objects.filter(created_at__gte=day_ago).count()
        
        # Последние активные пользователи
        recent_active_users = TelegramUser.objects.filter(
            messages__created_at__gte=day_ago
        ).distinct().order_by('-updated_at')[:10]
        
        # Последние сообщения
        recent_messages = TelegramMessage.objects.select_related('user').order_by('-created_at')[:20]
        
        # Статистика по типам сообщений
        message_types = TelegramMessage.objects.values('message_type').annotate(
            count=Count('id')
        ).order_by('-count')
        
        # Топ пользователей по активности
        top_users = TelegramUser.objects.annotate(
            message_count=Count('messages')
        ).filter(message_count__gt=0).order_by('-message_count')[:10]
        
        # Активность по часам (последние 24 часа)
        hourly_activity = []
        for i in range(24):
            hour_start = timezone.now() - timedelta(hours=23-i)
            hour_end = hour_start + timedelta(hours=1)
            count = TelegramMessage.objects.filter(
                created_at__gte=hour_start,
                created_at__lt=hour_end
            ).count()
            hourly_activity.append({
                'hour': hour_start.hour,
                'count': count
            })
        
        context = {
            # Общая статистика
            'total_users': total_users,
            'active_users': active_users,
            'total_messages': total_messages,
            
            # Статистика за неделю
            'new_users_week': new_users_week,
            'messages_week': messages_week,
            
            # Статистика за день
            'new_users_day': new_users_day,
            'messages_day': messages_day,
            
            # Активность
            'recent_active_users': recent_active_users,
            'recent_messages': recent_messages,
            'message_types': message_types,
            'top_users': top_users,
            'hourly_activity': hourly_activity,
            
            # Статус бота
            'bot_status': 'active',  # Можно добавить реальную проверку статуса
        }
        
        return render(request, 'telegrambot/dashboard.html', context)
        
    except Exception as e:
        logger.error(f"Ошибка получения данных dashboard: {e}")
        return JsonResponse({'error': str(e)}, status=500)
