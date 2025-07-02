import logging
import os
import uuid
import django
from datetime import datetime
from dotenv import load_dotenv
from telegram import Update, ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
from telegram.error import Conflict
from urllib.parse import quote
import asyncio

# Django setup
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ai_zam.settings')
django.setup()
from .models import TelegramUser, TelegramMessage
from .services import generate_document_with_deepseek, handle_documents_command

load_dotenv()
TELEGRAM_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')
SESSION_ID = str(uuid.uuid4())[:8]
BOT_START_TIME = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

logging.basicConfig(
    format=f'%(asctime)s - [{SESSION_ID}] - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

def get_or_create_telegram_user(telegram_data):
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
    if not created:
        user.username = username
        user.first_name = first_name
        user.last_name = last_name
        user.save()
    return user

def save_telegram_message(user, content, message_type='text', is_from_user=True):
    return TelegramMessage.objects.create(
        user=user,
        content=content,
        message_type=message_type,
        is_from_user=is_from_user
    )

def get_document_keyboard():
    return ReplyKeyboardMarkup([
        [KeyboardButton("📄 ЛЗК"), KeyboardButton("📊 ВОР")],
        [KeyboardButton("📋 ТЗ"), KeyboardButton("❓ Опросный лист")],
        [KeyboardButton("🔍 Акт скрытых работ"), KeyboardButton("📝 Пояснительная записка")],
        [KeyboardButton("🔙 Назад в главное меню")]
    ], resize_keyboard=True, one_time_keyboard=False)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    chat_id = update.effective_chat.id
    try:
        django_user = get_or_create_telegram_user({
            'id': chat_id,
            'username': user.username,
            'first_name': user.first_name,
            'last_name': user.last_name
        })
        save_telegram_message(django_user, "/start", "command", True)
    except Exception as e:
        logger.error(f"Ошибка сохранения пользователя в Django: {e}")
    # Use static text and keyboard for document menu
    doc_menu_text = (
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
    display_name = getattr(user, 'first_name', None) or 'пользователь'
    await update.message.reply_text(
        f'Здравствуйте, {display_name}!\n\n'
        f'{doc_menu_text}\n\n'
        f'✍️ Выберите тип документа или напишите параметры для генерации.\n',
        reply_markup=get_document_keyboard(),
        parse_mode='Markdown'
    )

async def handle_document_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message:
        return
    message_text = update.message.text
    chat_id = update.effective_chat.id
    user = update.effective_user
    keyboard = get_document_keyboard()
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
    doc_buttons = ["📄 ЛЗК", "📊 ВОР", "📋 ТЗ", "❓ Опросный лист", "🔍 Акт скрытых работ", "📝 Пояснительная записка"]
    if message_text in doc_buttons:
        document_type = {
            "📄 ЛЗК": "лимитно-заборную карту (ЛЗК)",
            "📊 ВОР": "ведомость объемов работ (ВОР)",
            "📋 ТЗ": "техническое задание (ТЗ)",
            "❓ Опросный лист": "опросный лист для подрядчика",
            "🔍 Акт скрытых работ": "акт скрытых работ",
            "📝 Пояснительная записка": "пояснительную записку к проекту"
        }
        doc_name = document_type.get(message_text, "документ")
        response_text = (
            f"📋 **Генерация {doc_name}**\n\n"
            f"Пожалуйста, укажите параметры для генерации {doc_name.lower()}.\n\n"
            "💡 Пример: 'ЛЗК на бетон М300, арматура А500С, опалубка щитовая'"
        )
        await update.message.reply_text(response_text, reply_markup=keyboard, parse_mode='Markdown')
        return
    elif message_text == "🔙 Назад в главное меню":
        await start(update, context)
        return
    await update.message.reply_text("Генерирую документ...", reply_markup=keyboard)
    loop = asyncio.get_running_loop()
    doc_text = await loop.run_in_executor(None, generate_document_with_deepseek, message_text)
    await update.message.reply_text(doc_text, reply_markup=keyboard, parse_mode='Markdown')
    try:
        save_telegram_message(django_user, doc_text, "text", False)
    except Exception as e:
        logger.error(f"Ошибка сохранения ответа бота в Django: {e}")
    # Отправляем отдельное сообщение с кнопками для скачивания
    short_content = quote(doc_text[:1000])
    logger.info(f"Отправка кнопок для скачивания: {short_content[:100]}...")
    # Тестовая кнопка для отладки
    test_keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton("Тест", url="https://ya.ru")]
    ])
    await update.message.reply_text(
        "Тестовая кнопка:",
        reply_markup=test_keyboard
    )
    download_keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton("Скачать DOCX", url=f"https://ai-zam.ru/telegram/export-document/?format=docx&content={short_content}")],
        [InlineKeyboardButton("Скачать PDF", url=f"https://ai-zam.ru/telegram/export-document/?format=pdf&content={short_content}")],
        [InlineKeyboardButton("Скачать XLS", url=f"https://ai-zam.ru/telegram/export-document/?format=xls&content={short_content}")],
    ])
    await update.message.reply_text(
        "Вы можете скачать этот документ в нужном формате:",
        reply_markup=download_keyboard
    )

async def error_handler(update: object, context: ContextTypes.DEFAULT_TYPE) -> None:
    logger.error(f"Exception while handling an update: {context.error}")
    if isinstance(context.error, Conflict):
        logger.error("Обнаружен конфликт - другой экземпляр бота уже запущен")
        logger.info("Попробуйте остановить другие экземпляры бота или подождите несколько минут")

def setup_handlers(application: Application):
    application.add_handler(CommandHandler("start", start))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_document_message))
    application.add_error_handler(error_handler)

def validate_config():
    if not TELEGRAM_TOKEN:
        logger.error("Не найден токен бота! Убедитесь, что TELEGRAM_BOT_TOKEN установлен в .env файле")
        return False
    return True

def main() -> None:
    if not validate_config():
        return
    print(f"🚀 Запускаю бота...")
    print(f"📅 Время запуска: {BOT_START_TIME}")
    print(f"🔢 Session ID: {SESSION_ID}")
    print(f"🔑 Telegram Token: {TELEGRAM_TOKEN[:20] if TELEGRAM_TOKEN else 'НЕ УСТАНОВЛЕН'}...")
    application = Application.builder().token(TELEGRAM_TOKEN).build()
    setup_handlers(application)
    logger.info("Бот запускается в режиме polling...")
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