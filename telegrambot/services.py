import os
import logging
import requests
import json
from datetime import datetime
from dotenv import load_dotenv
from .models import TelegramUser, TelegramMessage
from ai.services import generate_weekly_menu, generate_daily_menu, format_menu_text, get_ai_response

# Загружаем переменные окружения
load_dotenv()

# Получаем токен бота
TELEGRAM_TOKEN = os.getenv('TELEGRAM_TOKEN')

if not TELEGRAM_TOKEN:
    logger.error("TELEGRAM_TOKEN не найден в переменных окружения!")
    logger.error("Убедитесь, что файл .env содержит строку: TELEGRAM_TOKEN=ваш_токен")

logger = logging.getLogger(__name__)

def send_telegram_message(chat_id, text, reply_markup=None):
    """Отправка сообщения в Telegram"""
    try:
        if not TELEGRAM_TOKEN:
            logger.error("TELEGRAM_TOKEN не установлен")
            return None
            
        url = f'https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage'
        payload = {
            'chat_id': chat_id,
            'text': text,
            'parse_mode': 'HTML'
        }
        
        if reply_markup:
            payload['reply_markup'] = reply_markup
        
        logger.info(f"Отправка сообщения в Telegram: chat_id={chat_id}, text={text[:50]}...")
        
        response = requests.post(url, data=payload)
        response.raise_for_status()
        
        result = response.json()
        logger.info(f"Ответ от Telegram API: {result}")
        
        return result
    except requests.exceptions.RequestException as e:
        logger.error(f"Ошибка HTTP запроса к Telegram API: {e}")
        return None
    except json.JSONDecodeError as e:
        logger.error(f"Ошибка декодирования JSON ответа от Telegram: {e}")
        return None
    except Exception as e:
        logger.error(f"Неожиданная ошибка отправки сообщения в Telegram: {e}")
        return None

def get_or_create_telegram_user(telegram_data):
    """Получение или создание пользователя Telegram"""
    telegram_id = telegram_data['id']
    username = telegram_data.get('username')
    first_name = telegram_data.get('first_name')
    last_name = telegram_data.get('last_name')
    
    user, created = TelegramUser.objects.get_or_create(
        telegram_id=telegram_id,
        defaults={
            'username': username,
            'first_name': first_name,
            'last_name': last_name,
        }
    )
    
    # Обновляем данные пользователя
    if not created:
        user.username = username
        user.first_name = first_name
        user.last_name = last_name
        user.save()
    
    return user

def save_telegram_message(user, content, message_type='text', is_from_user=True):
    """Сохранение сообщения в базу данных"""
    return TelegramMessage.objects.create(
        user=user,
        content=content,
        message_type=message_type,
        is_from_user=is_from_user
    )

def handle_start_command(user):
    """Обработка команды /start"""
    welcome_text = (
        f"👨‍🍳 Здравствуйте, {user.first_name or 'пользователь'}! Я ваш помощник-повар.\n\n"
        "🍽️ Помогу составить меню и список покупок.\n\n"
        "✍️ Напишите ваши предпочтения в питании (например: \"без мяса\", \"люблю рыбу\", \"нет ограничений\") и нажмите кнопку!\n\n"
        "🔧 Команды:\n"
        "/menu_today - Меню на сегодня\n"
        "/menu_week - Меню на неделю\n"
        "/chat - Общий чат с AI\n"
        "/help - Помощь"
    )
    
    # Создаем клавиатуру с кнопками
    keyboard = {
        "keyboard": [
            [{"text": "🍳 Меню на день"}, {"text": "📅 Меню на неделю"}],
            [{"text": "💬 Общий чат"}, {"text": "❓ Помощь"}]
        ],
        "resize_keyboard": True,
        "one_time_keyboard": False
    }
    
    return welcome_text, keyboard

def handle_menu_today_command(user):
    """Обработка команды /menu_today"""
    text = (
        "Напишите ваши предпочтения в питании для меню на сегодня.\n\n"
        "💡 Если у вас нет особых предпочтений, напишите \"нет ограничений\"!"
    )
    
    # Сохраняем состояние пользователя (можно добавить поле в модель)
    return text, None

def handle_menu_week_command(user):
    """Обработка команды /menu_week"""
    text = (
        "Напишите ваши предпочтения в питании для меню на неделю.\n\n"
        "💡 Если у вас нет особых предпочтений, напишите \"нет ограничений\"!"
    )
    
    return text, None

def handle_help_command(user):
    """Обработка команды /help"""
    help_text = (
        "🤖 **Помощь по использованию бота:**\n\n"
        "🍽️ **Генерация меню:**\n"
        "• Нажмите кнопку \"🍳 Меню на день\" или \"📅 Меню на неделю\"\n"
        "• Укажите ваши предпочтения (например: \"вегетарианское\", \"без глютена\", \"люблю рыбу\")\n\n"
        "💬 **Общий чат:**\n"
        "• Нажмите кнопку \"💬 Общий чат\"\n"
        "• Задавайте любые вопросы AI ассистенту\n\n"
        "🔧 **Команды:**\n"
        "/start - Главное меню\n"
        "/menu_today - Меню на сегодня\n"
        "/menu_week - Меню на неделю\n"
        "/chat - Общий чат\n"
        "/help - Эта справка\n\n"
        "💡 **Примеры предпочтений:**\n"
        "• \"вегетарианское питание\"\n"
        "• \"без мяса, люблю рыбу\"\n"
        "• \"низкокалорийное меню\"\n"
        "• \"быстрое приготовление\"\n"
        "• \"экономное меню\""
    )
    
    return help_text, None

def handle_text_message(user, text):
    """Обработка текстовых сообщений"""
    # Проверяем, является ли это ответом на запрос меню
    if text in ["🍳 Меню на день", "📅 Меню на неделю"]:
        if text == "🍳 Меню на день":
            return handle_menu_today_command(user)
        else:
            return handle_menu_week_command(user)
    
    elif text == "💬 Общий чат":
        return "Отлично! Теперь вы можете задавать мне любые вопросы. Я буду отвечать как AI ассистент.", None
    
    elif text == "❓ Помощь":
        return handle_help_command(user)
    
    else:
        # Определяем тип запроса по контексту
        # Получаем последние сообщения пользователя для контекста
        recent_messages = list(user.messages.filter(is_from_user=True).order_by('-created_at')[:3])
        
        # Если последнее сообщение было о меню, генерируем меню
        if recent_messages and any("меню" in msg.content.lower() for msg in recent_messages):
            if any("неделю" in msg.content.lower() for msg in recent_messages):
                # Генерация меню на неделю
                menu_text = generate_weekly_menu(text)
                formatted_menu = format_menu_text(menu_text)
                return formatted_menu, None
            else:
                # Генерация меню на день
                menu_text = generate_daily_menu(text)
                formatted_menu = format_menu_text(menu_text)
                return formatted_menu, None
        else:
            # Общий чат с AI
            try:
                # Преобразуем QuerySet в список для безопасной передачи
                messages_list = list(recent_messages) if recent_messages else []
                ai_response = get_ai_response(text, messages_list)
                return ai_response, None
            except Exception as e:
                logger.error(f"Ошибка в AI чате: {e}")
                return f"❌ Ошибка при обработке сообщения: {str(e)}", None

def process_telegram_update(update_data):
    """Основная функция обработки обновлений от Telegram"""
    try:
        logger.info(f"Начало обработки обновления: {update_data}")
        
        message = update_data.get('message', {})
        chat_id = message.get('chat', {}).get('id')
        text = message.get('text', '')
        from_user = message.get('from', {})
        
        logger.info(f"Извлеченные данные: chat_id={chat_id}, text='{text}', from_user={from_user}")
        
        if not chat_id or not text:
            logger.warning(f"Пропуск обновления: chat_id={chat_id}, text='{text}'")
            return False
        
        # Получаем или создаем пользователя
        try:
            user = get_or_create_telegram_user(from_user)
            logger.info(f"Пользователь получен/создан: {user}")
        except Exception as e:
            logger.error(f"Ошибка получения пользователя: {e}")
            return False
        
        # Сохраняем сообщение пользователя
        try:
            save_telegram_message(user, text, 'text', True)
            logger.info("Сообщение пользователя сохранено")
        except Exception as e:
            logger.error(f"Ошибка сохранения сообщения пользователя: {e}")
            return False
        
        # Обрабатываем команды
        try:
            if text.startswith('/'):
                if text == '/start':
                    response_text, keyboard = handle_start_command(user)
                elif text == '/menu_today':
                    response_text, keyboard = handle_menu_today_command(user)
                elif text == '/menu_week':
                    response_text, keyboard = handle_menu_week_command(user)
                elif text == '/help':
                    response_text, keyboard = handle_help_command(user)
                else:
                    response_text = "❌ Неизвестная команда. Используйте /help для справки."
                    keyboard = None
            else:
                # Обрабатываем текстовые сообщения
                response_text, keyboard = handle_text_message(user, text)
            
            logger.info(f"Обработка завершена: response_text='{response_text[:50]}...', keyboard={keyboard is not None}")
        except Exception as e:
            logger.error(f"Ошибка обработки сообщения: {e}")
            return False
        
        # Сохраняем ответ бота
        if response_text:
            try:
                save_telegram_message(user, response_text, 'text', False)
                logger.info("Ответ бота сохранен")
            except Exception as e:
                logger.error(f"Ошибка сохранения ответа бота: {e}")
                # Не возвращаем False, продолжаем отправку
        
        # Отправляем ответ
        try:
            logger.info(f"Отправка сообщения: chat_id={chat_id}, text='{response_text[:50]}...'")
            result = send_telegram_message(chat_id, response_text, keyboard)
            
            logger.info(f"Результат отправки: {result}")
            
            # Безопасная проверка результата
            if result is None:
                logger.error("send_telegram_message вернул None")
                return False
            elif isinstance(result, dict):
                if result.get('ok'):
                    logger.info("Сообщение успешно отправлено")
                    return True
                else:
                    logger.error(f"Telegram API вернул ошибку: {result}")
                    return False
            else:
                logger.error(f"Неожиданный тип результата: {type(result)} = {result}")
                return False
                
        except Exception as e:
            logger.error(f"Исключение при отправке сообщения: {e}")
            return False
        
    except Exception as e:
        logger.error(f"Общая ошибка обработки Telegram обновления: {e}")
        return False 