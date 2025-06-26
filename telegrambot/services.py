import os
import logging
import requests
from datetime import datetime
from dotenv import load_dotenv
from .models import TelegramUser, TelegramMessage
from ai.services import generate_weekly_menu, generate_daily_menu, format_menu_text, get_ai_response

# Загружаем переменные окружения
load_dotenv()

# Получаем токен бота
TELEGRAM_TOKEN = os.getenv('TELEGRAM_TOKEN')

logger = logging.getLogger(__name__)

def send_telegram_message(chat_id, text, reply_markup=None):
    """Отправка сообщения в Telegram"""
    try:
        url = f'https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage'
        payload = {
            'chat_id': chat_id,
            'text': text,
            'parse_mode': 'HTML'
        }
        
        if reply_markup:
            payload['reply_markup'] = reply_markup
        
        response = requests.post(url, data=payload)
        response.raise_for_status()
        
        return response.json()
    except Exception as e:
        logger.error(f"Ошибка отправки сообщения в Telegram: {e}")
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
            ai_response = get_ai_response(text, recent_messages)
            return ai_response, None

def process_telegram_update(update_data):
    """Основная функция обработки обновлений от Telegram"""
    try:
        message = update_data.get('message', {})
        chat_id = message.get('chat', {}).get('id')
        text = message.get('text', '')
        from_user = message.get('from', {})
        
        if not chat_id or not text:
            return None
        
        # Получаем или создаем пользователя
        user = get_or_create_telegram_user(from_user)
        
        # Сохраняем сообщение пользователя
        save_telegram_message(user, text, 'text', True)
        
        # Обрабатываем команды
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
        
        # Сохраняем ответ бота
        if response_text:
            save_telegram_message(user, response_text, 'text', False)
        
        # Отправляем ответ
        return send_telegram_message(chat_id, response_text, keyboard)
        
    except Exception as e:
        logger.error(f"Ошибка обработки Telegram обновления: {e}")
        return None 