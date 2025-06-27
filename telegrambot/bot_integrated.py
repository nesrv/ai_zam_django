import logging
import os
import asyncio
import uuid
import time
import django
from datetime import datetime
from dotenv import load_dotenv
from openai import OpenAI
from telegram import Update, ReplyKeyboardMarkup, KeyboardButton
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
from telegram.error import Conflict

# Настройка Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ai_zam.settings')
django.setup()

# Импорты Django после настройки
from django.db import connection
from .models import TelegramUser, TelegramMessage

# Загружаем переменные окружения
load_dotenv()

# Конфигурация
TELEGRAM_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')
DEEPSEEK_API_KEY = os.getenv('DEEPSEEK_API_KEY')
DEEPSEEK_BASE_URL = "https://api.deepseek.com"

# Глобальные переменные
SESSION_ID = str(uuid.uuid4())[:8]
BOT_START_TIME = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
user_timers = {}  # Словарь для отслеживания автогенерации

# Настройка логирования
logging.basicConfig(
    format=f'%(asctime)s - [{SESSION_ID}] - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

def get_or_create_telegram_user(telegram_data):
    """Получение или создание пользователя Telegram в Django"""
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
    """Сохранение сообщения в Django базу данных"""
    return TelegramMessage.objects.create(
        user=user,
        content=content,
        message_type=message_type,
        is_from_user=is_from_user
    )

# Клавиатура
def get_keyboard():
    """Возвращает стандартную клавиатуру"""
    return ReplyKeyboardMarkup([
        [KeyboardButton("📅 Неделя"), KeyboardButton("🍽️ Сегодня")]
    ], resize_keyboard=True, one_time_keyboard=False)

def generate_menu(preferences, menu_type="неделя"):
    """Генерирует меню через DeepSeek API"""
    try:
        logger.info("Подключаюсь к DeepSeek...")
        client = OpenAI(api_key=DEEPSEEK_API_KEY, base_url=DEEPSEEK_BASE_URL)

        if menu_type == "сегодня":
            prompt = f"""Составь меню на один день для семьи из 4 человек, учитывая предпочтения: {preferences}.
            Укажи завтрак, обед, ужин и список покупок. Используй только тире (-) для списков."""
        else:
            prompt = f"""Составь меню на неделю для семьи из 4 человек, учитывая предпочтения: {preferences}.
            Укажи завтрак, обед, ужин для каждого дня и список покупок на всю неделю. Используй только тире (-) для списков."""

        response = client.chat.completions.create(
            model="deepseek-chat",
            messages=[
                {"role": "system", "content": "Ты опытный повар с 20-летним стажем."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.7,
            max_tokens=2000
        )

        menu_content = response.choices[0].message.content
        if menu_content:
            logger.info(f"Меню сгенерировано, длина: {len(menu_content)} символов")
        return menu_content

    except Exception as e:
        error_msg = f"Ошибка при работе с DeepSeek: {str(e)}"
        logger.error(error_msg)
        return error_msg

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработчик команды /start"""
    keyboard = get_keyboard()
    user = update.effective_user
    chat_id = update.effective_chat.id

    logger.info(f"👤 Пользователь {user.first_name} (ID: {chat_id}) запустил команду /start")

    # Сохраняем пользователя в Django
    try:
        django_user = get_or_create_telegram_user({
            'id': chat_id,
            'username': user.username,
            'first_name': user.first_name,
            'last_name': user.last_name
        })
        
        # Сохраняем сообщение
        save_telegram_message(django_user, "/start", "command", True)
        
    except Exception as e:
        logger.error(f"Ошибка сохранения пользователя в Django: {e}")

    await update.message.reply_text(
        f'*👨‍🍳 Привет, {user.first_name}! Я твой персональный шеф-повар!* 🎉\n\n'
        f'🍽️ *Готов превратить твои кулинарные мечты в реальность!*\n'
        f'✨ Создам идеальное меню и список покупок\n'
        f'🎯 Учту все твои вкусы и предпочтения\n\n'
        f'🚀 *Начнем кулинарное приключение?*\n\n'
        f'🔧 *Магия доступна через команды:*\n'
        f'🍳 `/today` - Меню на сегодня *(быстро и вкусно)*\n'
        f'📅 `/week` - Меню на неделю *(полный план питания)*\n'
        f'📊 `/stats` - Статистика бота\n'
        f'❓ `/help` - Справка и подсказки\n\n'
        f'💡 *Просто напиши свои предпочтения и нажми кнопку!*\n\n'
        f'🔢 Session ID: `{SESSION_ID}`\n'
        f'⏰ Запущен: `{BOT_START_TIME}`',
        reply_markup=keyboard,
        parse_mode='Markdown'
    )

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработчик команды /help"""
    help_text = """
🎭 *КУЛИНАРНЫЙ ТЕАТР* - Твои команды:

🍳 *`/today`* - Меню на сегодня
   Быстрое и вкусное меню для одного дня

📅 *`/week`* - Меню на неделю  
   Полный план питания на 7 дней

📊 *`/stats`* - Статистика бота
   Интересные цифры и факты

❓ *`/help`* - Эта справка
   Всегда здесь для тебя

🎯 *Как использовать:*
1. Выбери команду или нажми кнопку
2. Напиши предпочтения *(например: "люблю рыбу", "без мяса", "быстрое приготовление")*
3. Получи идеальное меню! ✨
    """
    await update.message.reply_text(help_text, parse_mode='Markdown')

async def today_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Команда для меню на сегодня"""
    keyboard = get_keyboard()
    chat_id = update.effective_chat.id
    user = update.effective_user
    
    await update.message.reply_text(
        f"🍳 *{user.first_name}, готовлю для тебя идеальное меню на сегодня!*\n\n"
        f"✨ *Напиши свои предпочтения:*\n"
        f"• Любимые продукты\n"
        f"• Диетические ограничения\n"
        f"• Время на готовку\n"
        f"• Любые пожелания",
        reply_markup=keyboard,
        parse_mode='Markdown'
    )
    
    context.user_data['menu_type'] = "🍽️ Сегодня"

async def week_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Команда для меню на неделю"""
    keyboard = get_keyboard()
    chat_id = update.effective_chat.id
    user = update.effective_user
    
    await update.message.reply_text(
        f"📅 *{user.first_name}, планирую твое идеальное питание на неделю!*\n\n"
        f"🌟 *Расскажи о своих предпочтениях:*\n"
        f"• Любимые кухни мира\n"
        f"• Продукты которые нравятся/не нравятся\n"
        f"• Диетические цели\n"
        f"• Бюджет на продукты",
        reply_markup=keyboard,
        parse_mode='Markdown'
    )
    
    context.user_data['menu_type'] = "📅 Неделя"

async def stats(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Команда для проверки статистики бота"""
    current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    
    # Получаем статистику из Django
    try:
        total_users = TelegramUser.objects.count()
        active_users = TelegramUser.objects.filter(is_active=True).count()
        total_messages = TelegramMessage.objects.count()
    except Exception as e:
        logger.error(f"Ошибка получения статистики из Django: {e}")
        total_users = 0
        active_users = 0
        total_messages = 0
    
    stats_text = (
        f"📊 *КУЛИНАРНАЯ СТАТИСТИКА* 📊\n\n"
        f"🤖 *Бот-шеф работает:*\n"
        f"🔢 Session ID: `{SESSION_ID}`\n"
        f"⏰ Запущен: `{BOT_START_TIME}`\n"
        f"📅 Текущее время: `{current_time}`\n\n"
        f"👥 *Активность:*\n"
        f"👨‍🍳 Поваров в очереди: `{total_users}`\n"
        f"🍽️ Меню создано: `{total_messages}`\n"
        f"👤 Активных пользователей: `{active_users}`\n\n"
        f"💡 *Готов создавать новые кулинарные шедевры!* ✨"
    )
    
    logger.info(f"📊 Запрошена статистика бота пользователем {update.effective_chat.id}")
    await update.message.reply_text(stats_text, parse_mode='Markdown')

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработчик всех текстовых сообщений"""
    message_text = update.message.text
    chat_id = update.effective_chat.id
    user = update.effective_user
    keyboard = get_keyboard()

    # Сохраняем сообщение пользователя в Django
    try:
        django_user = get_or_create_telegram_user({
            'id': chat_id,
            'username': user.username,
            'first_name': user.first_name,
            'last_name': user.last_name
        })
        
        save_telegram_message(django_user, message_text, "text", True)
        
    except Exception as e:
        logger.error(f"Ошибка сохранения сообщения в Django: {e}")

    # Проверяем, нажата ли кнопка
    if message_text in ["📅 Неделя", "🍽️ Сегодня"]:
        await update.message.reply_text(
            "*Напишите ваши предпочтения в питании.*",
            reply_markup=keyboard,
            parse_mode='Markdown'
        )
        context.user_data['menu_type'] = message_text
        return

    # Получаем предпочтения и генерируем меню
    preferences = message_text.lower()
    menu_type = context.user_data.get('menu_type', '📅 Неделя')

    # Генерируем и отправляем меню
    if menu_type == "🍽️ Сегодня":
        await update.message.reply_text("*Генерирую меню на сегодня...* 🍳", reply_markup=keyboard, parse_mode='Markdown')
        menu_text = generate_menu(preferences, "сегодня")
    else:
        await update.message.reply_text("*Генерирую меню на неделю...* 📅", reply_markup=keyboard, parse_mode='Markdown')
        menu_text = generate_menu(preferences, "неделя")

    try:
        await update.message.reply_text(
            f"🎨 *КУЛИНАРНОЕ МЕНЮ* 🎨\n\n{menu_text}\n\n✨ *Приятного аппетита!* ✨",
            reply_markup=keyboard,
            parse_mode='Markdown'
        )
        
        # Сохраняем ответ бота в Django
        try:
            save_telegram_message(django_user, menu_text, "text", False)
        except Exception as e:
            logger.error(f"Ошибка сохранения ответа бота в Django: {e}")
            
    except Exception as e:
        logger.error(f"Ошибка: {e}")
        await update.message.reply_text("*Ошибка генерации меню* ❌", reply_markup=keyboard, parse_mode='Markdown')

async def error_handler(update: object, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Обработчик ошибок"""
    logger.error(f"Exception while handling an update: {context.error}")
    
    if isinstance(context.error, Conflict):
        logger.error("Обнаружен конфликт - другой экземпляр бота уже запущен")
        logger.info("Попробуйте остановить другие экземпляры бота или подождите несколько минут")

def setup_handlers(application: Application):
    """Настраивает обработчики команд"""
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(CommandHandler("today", today_menu))
    application.add_handler(CommandHandler("week", week_menu))
    application.add_handler(CommandHandler("stats", stats))
    
    # Обработчик текстовых сообщений
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    application.add_error_handler(error_handler)

def validate_config():
    """Проверяет конфигурацию"""
    if not TELEGRAM_TOKEN:
        logger.error("Не найден токен бота! Убедитесь, что TELEGRAM_BOT_TOKEN установлен в .env файле")
        return False

    if not DEEPSEEK_API_KEY:
        logger.error("Не найден DeepSeek API ключ! Убедитесь, что DEEPSEEK_API_KEY установлен в .env файле")
        return False
    
    return True

def main() -> None:
    """Основная функция запуска бота"""
    if not validate_config():
        return

    print(f"🚀 Запускаю бота...")
    print(f"📅 Время запуска: {BOT_START_TIME}")
    print(f"🔢 Session ID: {SESSION_ID}")
    print(f"🔑 Telegram Token: {TELEGRAM_TOKEN[:20] if TELEGRAM_TOKEN else 'НЕ УСТАНОВЛЕН'}...")
    print(f"🔑 DeepSeek API Key: {'Установлен' if DEEPSEEK_API_KEY else 'НЕ УСТАНОВЛЕН'}")

    # Создаем и настраиваем приложение
    application = Application.builder().token(TELEGRAM_TOKEN).build()
    setup_handlers(application)

    # Запускаем бота
    logger.info("Бот запускается...")
    try:
        application.run_polling(
            drop_pending_updates=True,
            allowed_updates=Update.ALL_TYPES,
            close_loop=False
        )
    except Conflict as e:
        logger.error(f"Конфликт при запуске бота: {e}")
        logger.info("Другой экземпляр бота уже запущен. Остановите его или подождите несколько минут.")
    except Exception as e:
        logger.error(f"Ошибка запуска бота: {e}")

if __name__ == '__main__':
    main() 