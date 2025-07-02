import os
import logging
import requests
import json
from datetime import datetime
from dotenv import load_dotenv
from .models import TelegramUser, TelegramMessage
from ai.services import get_ai_response
import asyncio
import threading
from django.conf import settings
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
from telegram import (
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    ReplyKeyboardRemove,
)
from telegram.ext import (
    CallbackQueryHandler,
    ConversationHandler,
)
from asgiref.sync import sync_to_async

logger = logging.getLogger(__name__)

# Загружаем переменные окружения
load_dotenv()

# Получаем токен бота
TELEGRAM_TOKEN = os.getenv('TELEGRAM_TOKEN')

if not TELEGRAM_TOKEN:
    logger.error("TELEGRAM_TOKEN не найден в переменных окружения!")
    logger.error("Убедитесь, что файл .env содержит строку: TELEGRAM_TOKEN=ваш_токен")

# Токен бота
BOT_TOKEN = "7836693206:AAE_wRnOiWm0xhRlP7cr8Q0AvaPEgZCgTFw"

# Глобальные переменные для хранения экземпляров ботов
ne_srv_bot_app = None

# Асинхронные версии функций для работы с базой данных
@sync_to_async
def get_or_create_telegram_user_async(telegram_id, username, first_name, last_name):
    """Асинхронная версия получения или создания пользователя"""
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
        user.is_active = True
        user.save()
    
    return user

@sync_to_async
def save_telegram_message_async(user, content, message_type='text', is_from_user=True):
    """Асинхронная версия сохранения сообщения"""
    return TelegramMessage.objects.create(
        user=user,
        content=content,
        message_type=message_type,
        is_from_user=is_from_user
    )

def check_bot_token(token):
    """Проверка токена бота"""
    try:
        url = f'https://api.telegram.org/bot{token}/getMe'
        response = requests.get(url)
        response.raise_for_status()
        
        result = response.json()
        if result.get('ok'):
            bot_info = result.get('result', {})
            logger.info(f"Бот проверен: {bot_info.get('first_name')} (@{bot_info.get('username')})")
            return True, bot_info
        else:
            logger.error(f"Ошибка проверки токена: {result}")
            return False, result
    except Exception as e:
        logger.error(f"Ошибка проверки токена бота: {e}")
        return False, str(e)

def send_telegram_message(chat_id, text, reply_markup=None):
    """Отправка сообщения в Telegram"""
    try:
        # Используем BOT_TOKEN вместо TELEGRAM_TOKEN
        token = BOT_TOKEN or TELEGRAM_TOKEN
        if not token:
            logger.error("Токен бота не установлен")
            return None
        
        # Проверяем токен при первой отправке
        if not hasattr(send_telegram_message, '_token_checked'):
            is_valid, bot_info = check_bot_token(token)
            if not is_valid:
                logger.error(f"Недействительный токен бота: {bot_info}")
                return None
            send_telegram_message._token_checked = True
            
        url = f'https://api.telegram.org/bot{token}/sendMessage'
        payload = {
            'chat_id': chat_id,
            'text': text,
            'parse_mode': 'HTML'
        }
        
        if reply_markup:
            payload['reply_markup'] = json.dumps(reply_markup)
        
        logger.info(f"Отправка сообщения в Telegram: chat_id={chat_id}, text={text[:50]}...")
        
        response = requests.post(url, data=payload)
        
        # Получаем ответ для анализа ошибки
        response_text = response.text
        logger.info(f"Ответ от Telegram API (статус {response.status_code}): {response_text}")
        
        if response.status_code == 400:
            # Пытаемся получить подробную информацию об ошибке
            try:
                error_data = response.json()
                error_code = error_data.get('error_code', 'unknown')
                description = error_data.get('description', 'No description')
                logger.error(f"Ошибка 400: код={error_code}, описание={description}")
                
                # Обрабатываем специфические ошибки
                if error_code == 400:
                    if "chat not found" in description.lower():
                        logger.error(f"Чат {chat_id} не найден - возможно, пользователь заблокировал бота")
                    elif "user not found" in description.lower():
                        logger.error(f"Пользователь {chat_id} не найден")
                    elif "bot was blocked" in description.lower():
                        logger.error(f"Бот заблокирован пользователем {chat_id}")
                    else:
                        logger.error(f"Неизвестная ошибка 400: {description}")
                
                return {'ok': False, 'error_code': error_code, 'description': description}
            except:
                logger.error(f"Не удалось разобрать ответ об ошибке: {response_text}")
                return {'ok': False, 'error': 'Failed to parse error response'}
        
        response.raise_for_status()
        
        result = response.json()
        logger.info(f"Успешный ответ от Telegram API: {result}")
        
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

def handle_start_command(user):
    """Обработка команды /start"""
    welcome_text = (
        f"Здравствуйте, {user.first_name or 'пользователь'}! Я ваш виртуальный помощник.\n\n"
        "📋 Могу генерировать строительные документы!\n\n"
        "✍️ Просто выберите тип документа или напишите параметры для генерации.\n\n"
        "🔧 Команды:\n"
        "/documents - Генерация документов\n"
        "/chat - Общий чат с AI\n"
        "/help - Помощь"
    )
    keyboard = {
        "keyboard": [
            [{"text": "💬 Общий чат"}, {"text": "📋 Генерация документов"}],
            [{"text": "❓ Помощь"}]
        ],
        "resize_keyboard": True,
        "one_time_keyboard": False
    }
    return welcome_text, keyboard

def handle_help_command(user):
    help_text = (
        "📋 **Генерация строительных документов**\n\n"
        "Выберите тип документа для генерации:\n\n"
        "📄 **Лимитно-заборная карта (ЛЗК)**\n"
        "• Для учета материалов и оборудования\n"
        "• Укажите название материала/оборудования\n\n"
        "📊 **Ведомость объемов работ (ВОР)**\n"
        "• Для планирования строительных работ\n"
        "• Укажите тип объекта/этап строительства\n\n"
        "📋 **Техническое задание (ТЗ)**\n"
        "• Для проектирования объектов/систем\n"
        "• Укажите объект/систему для проектирования\n\n"
        "❓ **Опросный лист для подрядчика**\n"
        "• Для подготовки к тендерам\n"
        "• Укажите вид работ\n\n"
        "🔍 **Акт скрытых работ**\n"
        "• Для приемки скрытых работ\n"
        "• Укажите вид работ\n\n"
        "📝 **Пояснительная записка к проекту**\n"
        "• Подробное описание проекта\n\n"
        "💡 **Примеры запросов:**\n"
        "• 'ЛЗК на бетон М300, арматура А500С'\n"
        "• 'ВОР для строительства жилого дома'\n"
        "• 'ТЗ на проектирование системы отопления'"
    )
    return help_text, None

def handle_documents_command(user):
    """Обработка команды генерации документов"""
    text = (
        "📋 **Генерация строительных документов**\n\n"
        "Выберите тип документа для генерации:\n\n"
        "📄 **Лимитно-заборная карта (ЛЗК)**\n"
        "• Для учета материалов и оборудования\n"
        "• Укажите название материала/оборудования\n\n"
        "📊 **Ведомость объемов работ (ВОР)**\n"
        "• Для планирования строительных работ\n"
        "• Укажите тип объекта/этап строительства\n\n"
        "📋 **Техническое задание (ТЗ)**\n"
        "• Для проектирования объектов/систем\n"
        "• Укажите объект/систему для проектирования\n\n"
        "❓ **Опросный лист для подрядчика**\n"
        "• Для подготовки к тендерам\n"
        "• Укажите вид работ\n\n"
        "🔍 **Акт скрытых работ**\n"
        "• Для приемки скрытых работ\n"
        "• Укажите вид работ\n\n"
        "📝 **Пояснительная записка к проекту**\n"
        "• Подробное описание проекта\n\n"
        "💡 **Примеры запросов:**\n"
        "• 'ЛЗК на бетон М300, арматура А500С'\n"
        "• 'ВОР для строительства жилого дома'\n"
        "• 'ТЗ на проектирование системы отопления'"
    )
    
    # Создаем клавиатуру с кнопками документов
    keyboard = {
        "keyboard": [
            [{"text": "📄 ЛЗК"}, {"text": "📊 ВОР"}],
            [{"text": "📋 ТЗ"}, {"text": "❓ Опросный лист"}],
            [{"text": "🔍 Акт скрытых работ"}, {"text": "📝 Пояснительная записка"}],
            [{"text": "🔙 Назад в главное меню"}]
        ],
        "resize_keyboard": True,
        "one_time_keyboard": False
    }
    
    return text, keyboard

def handle_text_message(user, text):
    if text == "💬 Общий чат":
        return "Отлично! Теперь вы можете задавать мне любые вопросы. Я буду отвечать как AI ассистент.", None
    elif text == "📋 Генерация документов":
        return handle_documents_command(user)
    elif text == "❓ Помощь":
        return handle_help_command(user)
    elif text == "🔙 Назад в главное меню":
        return handle_start_command(user)
    elif text in ["📄 ЛЗК", "📊 ВОР", "📋 ТЗ", "❓ Опросный лист", "🔍 Акт скрытых работ", "📝 Пояснительная записка"]:
        document_type = {
            "📄 ЛЗК": "лимитно-заборную карту (ЛЗК)",
            "📊 ВОР": "ведомость объемов работ (ВОР)",
            "📋 ТЗ": "техническое задание (ТЗ)",
            "❓ Опросный лист": "опросный лист для подрядчика",
            "🔍 Акт скрытых работ": "акт скрытых работ",
            "📝 Пояснительная записка": "пояснительную записку к проекту"
        }
        doc_name = document_type.get(text, "документ")
        response_text = (
            f"📋 **Генерация {doc_name}**\n\n"
            f"Пожалуйста, укажите параметры для генерации {doc_name.lower()}.\n\n"
            "💡 **Примеры запросов:**\n"
        )
        if text == "📄 ЛЗК":
            response_text += "• 'ЛЗК на бетон М300, арматура А500С, опалубка щитовая'\n• 'Лимитно-заборная карта для кирпичной кладки'"
        elif text == "📊 ВОР":
            response_text += "• 'ВОР для строительства жилого дома'\n• 'Ведомость объемов работ для ремонта квартиры'"
        elif text == "📋 ТЗ":
            response_text += "• 'ТЗ на проектирование системы отопления'\n• 'Техническое задание для вентиляции'"
        elif text == "❓ Опросный лист":
            response_text += "• 'Опросный лист для электромонтажных работ'\n• 'Опросник для отделочных работ'"
        elif text == "🔍 Акт скрытых работ":
            response_text += "• 'Акт скрытых работ для электропроводки'\n• 'Акт для гидроизоляции фундамента'"
        elif text == "📝 Пояснительная записка":
            response_text += "• 'Пояснительная записка для проекта дома'\n• 'Описание проекта торгового центра'"
        return response_text, None
    else:
        # Общий чат с AI
        try:
            recent_messages = list(user.messages.filter(is_from_user=True).order_by('-created_at')[:3])
            messages_list = list(recent_messages) if recent_messages else []
            ai_response = get_ai_response(text, messages_list)
            return ai_response, None
        except Exception as e:
            logger.error(f"Ошибка в AI чате: {e}")
            return f"❌ Ошибка при обработке сообщения: {str(e)}", None

def process_telegram_update(update_data):
    """Обработка обновления от Telegram webhook"""
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
            if not from_user or 'id' not in from_user:
                logger.error("from_user отсутствует или не содержит id, пропуск обновления")
                return False
            user_data = {
                'id': from_user.get('id'),
                'username': from_user.get('username'),
                'first_name': from_user.get('first_name'),
                'last_name': from_user.get('last_name'),
            }
            user = get_or_create_telegram_user(user_data)
            if not user:
                logger.error("Не удалось получить или создать пользователя, пропуск обновления")
                return False
            logger.info(f"Пользователь получен/создан: {user}")
        except Exception as e:
            logger.error(f"Ошибка получения пользователя: {e}")
            return False
        
        # Сохраняем сообщение пользователя
        try:
            if not user:
                logger.error("user is None, пропуск сохранения сообщения пользователя")
                return False
            save_telegram_message(user, text, 'text', True)
            logger.info("Сообщение пользователя сохранено")
        except Exception as e:
            logger.error(f"Ошибка сохранения сообщения пользователя: {e}")
            return False
        
        # Обрабатываем команды
        try:
            if not user:
                logger.error("user is None, пропуск обработки команды")
                return False
            if text.startswith('/'):
                if text == '/start':
                    response_text, keyboard = handle_start_command(user)
                elif text == '/documents':
                    response_text, keyboard = handle_documents_command(user)
                elif text == '/help':
                    response_text, keyboard = handle_help_command(user)
                else:
                    response_text = "❌ Неизвестная команда. Используйте /help для справки."
                    keyboard = None
            else:
                response_text, keyboard = handle_text_message(user, text)
            logger.info(f"Обработка завершена: response_text='{response_text[:50]}...', keyboard={keyboard is not None}")
        except Exception as e:
            logger.error(f"Ошибка обработки сообщения: {e}")
            return False
        
        # Сохраняем ответ бота
        if response_text:
            try:
                if not user:
                    logger.error("user is None, пропуск сохранения ответа бота")
                else:
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

# ==================== NE_SRV_BOT ====================

# Обработчик команды /start для первого бота
async def ne_srv_start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    chat_id = update.effective_chat.id
    
    # Сохраняем пользователя
    telegram_user = await get_or_create_telegram_user_async(user.id, user.username, user.first_name, user.last_name)
    
    # Сохраняем сообщение
    await save_telegram_message_async(telegram_user, '/start', 'command', True)
    
    response = "Привет! Я тестовый бот. Напиши что-нибудь!"
    
    # Сохраняем ответ бота
    await save_telegram_message_async(telegram_user, response, 'text', False)
    
    await update.message.reply_text(response)

# Обработчик команды /help для первого бота
async def ne_srv_help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    
    # Получаем или создаем пользователя
    telegram_user = await get_or_create_telegram_user_async(user.id, user.username, user.first_name, user.last_name)
    
    # Сохраняем сообщение
    await save_telegram_message_async(telegram_user, '/help', 'command', True)
    
    response = """
    Доступные команды:
    /start - начать общение
    /help - помощь
    """
    
    # Сохраняем ответ бота
    await save_telegram_message_async(telegram_user, response, 'text', False)
    
    await update.message.reply_text(response)

# Обработчик обычных текстовых сообщений для первого бота
async def ne_srv_handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    user_message = update.message.text.lower()
    
    # Получаем или создаем пользователя
    telegram_user = await get_or_create_telegram_user_async(user.id, user.username, user.first_name, user.last_name)
    
    # Сохраняем сообщение пользователя
    await save_telegram_message_async(telegram_user, update.message.text, 'text', True)
    
    if "привет" in user_message:
        response = "Привет! Как дела?"
    elif "пока" in user_message:
        response = "До свидания! Возвращайся :)"
    else:
        response = "Я не понял сообщение. Попробуй /help"
    
    # Сохраняем ответ бота
    await save_telegram_message_async(telegram_user, response, 'text', False)
    
    await update.message.reply_text(response)

# Обработчик ошибок для первого бота
async def ne_srv_error(update: Update, context: ContextTypes.DEFAULT_TYPE):
    logger.error(f"NE_SRV_BOT Update {update} caused error {context.error}")

# ==================== ФУНКЦИИ ЗАПУСКА БОТА ====================

def start_ne_srv_bot_in_thread():
    """Запускает бота в отдельном потоке"""
    def run_bot():
        try:
            # Создаем новый event loop для потока
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            
            # Запускаем бота
            app = Application.builder().token(BOT_TOKEN).build()

            # Регистрация обработчиков команд
            app.add_handler(CommandHandler("start", ne_srv_start_command))
            app.add_handler(CommandHandler("help", ne_srv_help_command))

            # Регистрация обработчика текстовых сообщений
            app.add_handler(MessageHandler(filters.TEXT, ne_srv_handle_message))

            # Регистрация обработчика ошибок
            app.add_error_handler(ne_srv_error)

            logger.info("NE_SRV_BOT запущен и работает...")
            
            # Запускаем бота в бесконечном цикле
            loop.run_until_complete(app.run_polling(poll_interval=3))
            
        except Exception as e:
            logger.error(f'Ошибка в потоке NE_SRV_BOT: {e}')
    
    thread = threading.Thread(target=run_bot, daemon=True)
    thread.start()
    return thread

def start_all_bots():
    """Запускает ne_srv_bot в отдельном потоке"""
    logger.info("Запуск ne_srv_bot...")
    bot_thread = start_ne_srv_bot_in_thread()
    return bot_thread

def get_or_create_telegram_user(telegram_data):
    """Получение или создание пользователя Telegram (синхронная версия)"""
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
    """Сохранение сообщения в базу данных (синхронная версия)"""
    return TelegramMessage.objects.create(
        user=user,
        content=content,
        message_type=message_type,
        is_from_user=is_from_user
    )

def generate_document_with_deepseek(prompt):
    """
    Генерирует документ с помощью DeepSeek API
    """
    try:
        logger.info(f"Отправляю запрос к DeepSeek API с промптом: {prompt[:100]}...")
        
        # Для тестирования интерфейса используем заглушку
        if "test_mode" in prompt.lower():
            fake_response = f"""
📋 ДОКУМЕНТ (ТЕСТОВЫЙ РЕЖИМ)

Запрос: {prompt}

Это тестовый ответ от DeepSeek API. В реальном режиме здесь будет сгенерированный документ.

Пример структуры документа:
1. Заголовок
2. Основная часть
3. Заключение

Документ будет отправлен всем пользователям Telegram бота.
            """
            logger.info("Используется тестовый режим")
            return fake_response.strip()
        
        headers = {
            'Authorization': f'Bearer {settings.DEEPSEEK_API_KEY}',
            'Content-Type': 'application/json'
        }
        
        data = {
            'model': 'deepseek-chat',
            'messages': [
                {
                    'role': 'system',
                    'content': 'Ты опытный инженер-строитель и технический писатель. Твоя задача - создавать качественные строительные документы на русском языке.'
                },
                {
                    'role': 'user',
                    'content': prompt
                }
            ],
            'max_tokens': 2000,
            'temperature': 0.7
        }
        
        logger.info(f"Отправляю POST запрос к {settings.DEEPSEEK_BASE_URL}/v1/chat/completions")
        
        try:
            response = requests.post(
                f'{settings.DEEPSEEK_BASE_URL}/v1/chat/completions',
                headers=headers,
                json=data,
                timeout=60  # Увеличиваем таймаут до 60 секунд
            )
        except requests.exceptions.Timeout:
            error_msg = "Таймаут подключения к DeepSeek API. Попробуйте позже."
            logger.error(error_msg)
            return error_msg
        except requests.exceptions.ConnectionError:
            error_msg = "Ошибка подключения к DeepSeek API. Проверьте интернет-соединение."
            logger.error(error_msg)
            return error_msg
        except requests.exceptions.RequestException as e:
            error_msg = f"Ошибка сетевого запроса к DeepSeek API: {str(e)}"
            logger.error(error_msg)
            return error_msg
        
        logger.info(f"Получен ответ от DeepSeek API: статус {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            generated_content = result['choices'][0]['message']['content']
            logger.info(f"Успешно сгенерирован документ длиной {len(generated_content)} символов")
            return generated_content
        else:
            error_msg = f"Ошибка API: {response.status_code} - {response.text}"
            logger.error(error_msg)
            return error_msg
            
    except Exception as e:
        error_msg = f"Ошибка при генерации документа: {str(e)}"
        logger.error(error_msg)
        return error_msg 