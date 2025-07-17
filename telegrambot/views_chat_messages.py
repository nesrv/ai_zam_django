import json
import logging
from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from django.db.models import Count, Q
from django.utils import timezone
from datetime import timedelta
from .models import ChatMessage
from object.models import Objekt
from .services import send_telegram_message, BOT_TOKEN

logger = logging.getLogger(__name__)

def chat_messages_list(request):
    """Страница со списком всех чатов и их сообщений"""
    try:
        # Получаем все уникальные chat_id из сообщений
        chat_ids = ChatMessage.objects.values('chat_id').annotate(
            count=Count('id')
        ).order_by('-count')
        
        # Для каждого чата получаем информацию
        chats = []
        for chat_data in chat_ids:
            chat_id = chat_data['chat_id']
            message_count = chat_data['count']
            
            # Получаем последнее сообщение из чата
            last_message = ChatMessage.objects.filter(
                chat_id=chat_id
            ).order_by('-created_at').first()
            
            # Проверяем, связан ли чат с объектом
            objekt = None
            try:
                objekt = Objekt.objects.filter(chat_id=chat_id).first()
            except:
                pass
            
            chats.append({
                'chat_id': chat_id,
                'message_count': message_count,
                'last_message': last_message,
                'objekt': objekt,
                'last_activity': last_message.created_at if last_message else None
            })
        
        # Сортируем чаты по времени последней активности
        chats.sort(key=lambda x: x['last_activity'] if x['last_activity'] else timezone.now(), reverse=True)
        
        context = {
            'chats': chats,
            'total_chats': len(chats),
            'total_messages': ChatMessage.objects.count()
        }
        
        return render(request, 'telegrambot/chat_messages_list.html', context)
        
    except Exception as e:
        logger.error(f"Ошибка получения списка чатов: {e}")
        return JsonResponse({'error': str(e)}, status=500)

def chat_messages_detail(request, chat_id):
    """Страница с детальной информацией о чате и его сообщениях"""
    try:
        # Получаем сообщения из чата
        messages = ChatMessage.objects.filter(
            chat_id=chat_id
        ).order_by('created_at')
        
        # Проверяем, связан ли чат с объектом
        objekt = None
        try:
            objekt = Objekt.objects.filter(chat_id=chat_id).first()
        except:
            pass
        
        # Статистика чата
        stats = {
            'message_count': messages.count(),
            'first_message': messages.first(),
            'last_message': messages.last(),
            'unique_users': messages.values('from_user').distinct().count()
        }
        
        # Топ пользователей по количеству сообщений
        top_users = messages.values('from_user').annotate(
            count=Count('id')
        ).order_by('-count')[:10]
        
        context = {
            'chat_id': chat_id,
            'messages': messages,
            'objekt': objekt,
            'stats': stats,
            'top_users': top_users
        }
        
        return render(request, 'telegrambot/chat_messages_detail.html', context)
        
    except Exception as e:
        logger.error(f"Ошибка получения деталей чата {chat_id}: {e}")
        return JsonResponse({'error': str(e)}, status=500)

@csrf_exempt
@require_POST
def send_message_to_chat(request, chat_id):
    """Отправка сообщения в чат через бота"""
    try:
        data = json.loads(request.body)
        message = data.get('message', '').strip()
        
        if not message:
            return JsonResponse({
                'success': False,
                'error': 'Сообщение не может быть пустым'
            })
        
        # Отправляем сообщение через Telegram API
        result = send_telegram_message(chat_id, message)
        
        if result and result.get('ok'):
            return JsonResponse({
                'success': True,
                'message': 'Сообщение успешно отправлено'
            })
        else:
            return JsonResponse({
                'success': False,
                'error': f'Ошибка отправки сообщения: {result}'
            })
            
    except json.JSONDecodeError:
        return JsonResponse({
            'success': False,
            'error': 'Неверный формат JSON'
        })
    except Exception as e:
        logger.error(f"Ошибка отправки сообщения в чат {chat_id}: {e}")
        return JsonResponse({
            'success': False,
            'error': str(e)
        })

def get_chat_messages_ajax(request, chat_id):
    """AJAX-запрос для получения сообщений из чата"""
    try:
        # Получаем сообщения из чата
        messages = ChatMessage.objects.filter(
            chat_id=chat_id
        ).order_by('-created_at')[:50]
        
        messages_data = []
        for msg in reversed(messages):
            messages_data.append({
                'id': msg.id,
                'text': msg.message_text,
                'from_user': msg.from_user,
                'date': msg.created_at.strftime('%H:%M %d.%m.%Y'),
                'is_reply': msg.is_reply(),
                'is_forwarded': msg.is_forwarded()
            })
        
        return JsonResponse({
            'success': True,
            'messages': messages_data,
            'count': len(messages_data)
        })
        
    except Exception as e:
        logger.error(f"Ошибка получения сообщений из чата {chat_id}: {e}")
        return JsonResponse({
            'success': False,
            'error': str(e)
        })