from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse
from object.models import Objekt
import json
import os
import asyncio
import logging
from .models import ChatMessage, TelegramMessage, TelegramUser
from telegram import Bot
from dotenv import load_dotenv

load_dotenv()
logger = logging.getLogger(__name__)

async def get_chat_messages_from_bot(chat_id, bot_token):
    """Получение последних сообщений из чата через Telegram Bot API"""
    try:
        bot = Bot(token=bot_token)
        
        # Получаем информацию о чате
        try:
            chat = await bot.get_chat(chat_id)
            logger.info(f"Чат найден: {chat.title or chat.first_name} (ID: {chat_id})")
        except Exception as e:
            logger.error(f"Ошибка получения информации о чате {chat_id}: {e}")
            return []
        
        # Получаем последние обновления
        updates = await bot.get_updates(limit=100, allowed_updates=['message'])
        messages = []
        
        for update in updates:
            if (update.message and 
                str(update.message.chat.id) == str(chat_id) and 
                update.message.text):
                
                messages.append({
                    'text': update.message.text,
                    'date': update.message.date.strftime('%H:%M %d.%m'),
                    'from_user': (
                        update.message.from_user.first_name 
                        if update.message.from_user 
                        else 'Неизвестно'
                    ),
                    'message_id': update.message.message_id
                })
        
        # Сортируем по времени и берем последние 10
        messages.sort(key=lambda x: x['message_id'])
        return messages[-10:]
        
    except Exception as e:
        logger.error(f"Ошибка получения сообщений из чата {chat_id}: {e}")
        return []
    finally:
        try:
            await bot.session.close()
        except:
            pass

def chatbots_page(request):
    """Страница чат-ботов для объектов"""
    objekty = Objekt.objects.filter(is_active=True)
    bot_token = os.getenv('TELEGRAM_BOT_TOKEN') or os.getenv('TELEGRAM_TOKEN')
    
    # Получаем сообщения для объектов с chat_id
    for objekt in objekty:
        if objekt.chat_id and bot_token:
            try:
                # Получаем сообщения из ChatMessage (групповые чаты)
                chat_messages = ChatMessage.objects.filter(
                    chat_id=str(objekt.chat_id)
                ).order_by('-created_at')[:10]
                
                if chat_messages:
                    objekt.recent_messages = [
                        {
                            'text': msg.message_text,
                            'from_user': msg.from_user,
                            'date': msg.created_at.strftime('%H:%M %d.%m'),
                            'is_from_user': True  # Все сообщения из чатов - от пользователей
                        }
                        for msg in reversed(chat_messages)
                    ]
                else:
                    # Если нет сообщений в ChatMessage, проверяем TelegramMessage
                    telegram_messages = TelegramMessage.objects.filter(
                        user__telegram_id=objekt.chat_id
                    ).select_related('user').order_by('-created_at')[:10]
                    
                    if telegram_messages:
                        objekt.recent_messages = [
                            {
                                'text': msg.content,
                                'from_user': msg.user.first_name or 'Пользователь',
                                'date': msg.created_at.strftime('%H:%M %d.%m'),
                                'is_from_user': msg.is_from_user
                            }
                            for msg in reversed(telegram_messages)
                        ]
                    else:
                        objekt.recent_messages = []
                        
            except Exception as e:
                logger.error(f"Ошибка обработки чата для объекта {objekt.id}: {e}")
                objekt.recent_messages = []
        else:
            objekt.recent_messages = []
    
    # Добавляем статистику
    total_connected = sum(1 for obj in objekty if obj.chat_id)
    total_messages = TelegramMessage.objects.count()
    
    context = {
        'objekty': objekty,
        'total_connected': total_connected,
        'total_messages': total_messages,
        'bot_token_configured': bool(bot_token)
    }
    
    return render(request, 'telegrambot/chatbots.html', context)

def update_chat_id(request):
    """Обновление chat_id для объекта"""
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            objekt_id = data.get('objekt_id')
            chat_id = data.get('chat_id')
            
            objekt = get_object_or_404(Objekt, id=objekt_id)
            # Валидация chat_id
            if chat_id:
                # Проверяем, что chat_id является числом (для Telegram)
                try:
                    int(chat_id)
                except ValueError:
                    return JsonResponse({
                        'success': False, 
                        'error': 'Chat ID должен быть числом'
                    })
                
                # Проверяем, что такой chat_id еще не используется
                existing = Objekt.objects.filter(
                    chat_id=chat_id
                ).exclude(id=objekt_id).first()
                
                if existing:
                    return JsonResponse({
                        'success': False, 
                        'error': f'Chat ID уже используется объектом "{existing.nazvanie}"'
                    })
            
            objekt.chat_id = chat_id if chat_id else None
            objekt.save()
            
            logger.info(f"Chat ID {'установлен' if chat_id else 'удален'} для объекта {objekt.nazvanie}: {chat_id}")
            
            return JsonResponse({
                'success': True,
                'message': f'Chat ID {'подключен' if chat_id else 'отключен'} для объекта {objekt.nazvanie}'
            })
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)})
    
    return JsonResponse({'success': False, 'error': 'Invalid request method'})

def get_chat_messages_ajax(request):
    """AJAX получение сообщений из чата"""
    if request.method == 'GET':
        chat_id = request.GET.get('chat_id')
        if not chat_id:
            return JsonResponse({'success': False, 'error': 'Chat ID не указан'})
        
        try:
            # Получаем сообщения из ChatMessage (групповые чаты)
            chat_messages = ChatMessage.objects.filter(
                chat_id=str(chat_id)
            ).order_by('-created_at')[:10]
            
            if chat_messages:
                messages_data = [
                    {
                        'text': msg.message_text,
                        'from_user': msg.from_user,
                        'date': msg.created_at.strftime('%H:%M %d.%m'),
                        'is_from_user': True
                    }
                    for msg in reversed(chat_messages)
                ]
            else:
                # Проверяем TelegramMessage (личные чаты)
                telegram_messages = TelegramMessage.objects.filter(
                    user__telegram_id=chat_id
                ).select_related('user').order_by('-created_at')[:10]
                
                messages_data = [
                    {
                        'text': msg.content,
                        'from_user': msg.user.first_name or 'Пользователь',
                        'date': msg.created_at.strftime('%H:%M %d.%m'),
                        'is_from_user': msg.is_from_user
                    }
                    for msg in reversed(telegram_messages)
                ]
            
            return JsonResponse({
                'success': True,
                'messages': messages_data,
                'count': len(messages_data)
            })
            
        except Exception as e:
            logger.error(f"Ошибка получения сообщений: {e}")
            return JsonResponse({'success': False, 'error': str(e)})
    
    return JsonResponse({'success': False, 'error': 'Метод не поддерживается'})

def send_message_to_chat(request):
    """Отправка сообщения в чат через бота"""
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            chat_id = data.get('chat_id')
            message = data.get('message', '').strip()
            
            if not chat_id or not message:
                return JsonResponse({
                    'success': False, 
                    'error': 'Chat ID и сообщение обязательны'
                })
            
            # Отправляем сообщение через интегрированный бот
            from .services import send_telegram_message
            
            result = send_telegram_message(chat_id, message)
            
            if result and result.get('ok'):
                return JsonResponse({
                    'success': True,
                    'message': 'Сообщение отправлено'
                })
            else:
                return JsonResponse({
                    'success': False,
                    'error': f'Ошибка отправки: {result}'
                })
                
        except json.JSONDecodeError:
            return JsonResponse({'success': False, 'error': 'Неверный формат JSON'})
        except Exception as e:
            logger.error(f"Ошибка отправки сообщения: {e}")
            return JsonResponse({'success': False, 'error': str(e)})
    
    return JsonResponse({'success': False, 'error': 'Метод не поддерживается'})