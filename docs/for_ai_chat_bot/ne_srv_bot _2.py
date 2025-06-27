import logging
from datetime import datetime
from telegram import (
    Update,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    KeyboardButton,
    ReplyKeyboardMarkup,
    ReplyKeyboardRemove,
)
from telegram.ext import (
    Application,
    CommandHandler,
    CallbackQueryHandler,
    MessageHandler,
    filters,
    ContextTypes,
    ConversationHandler,
)

# Настройка логгирования
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
logger = logging.getLogger(__name__)

# Константы состояний для ConversationHandler
MENU, SUBMENU = range(2)

# Токен вашего бота (замените на ваш)
BOT_TOKEN = "7836693206:AAE_wRnOiWm0xhRlP7cr8Q0AvaPEgZCgTFw"

# Клавиатура для главного меню
def main_menu_keyboard():
    return [
        [
            InlineKeyboardButton("📅 Дата и время", callback_data="datetime"),
            InlineKeyboardButton("ℹ️ Информация", callback_data="info"),
        ],
        [
            InlineKeyboardButton("⚙️ Настройки", callback_data="settings"),
            InlineKeyboardButton("🆘 Помощь", callback_data="help"),
        ],
    ]

# Клавиатура для меню настроек
def settings_menu_keyboard():
    return [
        [
            InlineKeyboardButton("🔔 Уведомления", callback_data="notifications"),
            InlineKeyboardButton("🌍 Язык", callback_data="language"),
        ],
        [InlineKeyboardButton("⬅️ Назад", callback_data="back_to_main")],
    ]

# Обработчик команды /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    await update.message.reply_text(
        f"Привет, {user.first_name}! Я умный бот с расширенными функциями.\n"
        "Выберите действие из меню ниже:",
        reply_markup=InlineKeyboardMarkup(main_menu_keyboard()),
    )
    return MENU

# Обработчик нажатий на inline-кнопки
async def button_click(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    if query.data == "datetime":
        now = datetime.now()
        current_time = now.strftime("%H:%M:%S")
        current_date = now.strftime("%d.%m.%Y")
        await query.edit_message_text(
            f"🕒 Текущее время: {current_time}\n"
            f"📅 Сегодняшняя дата: {current_date}",
            reply_markup=InlineKeyboardMarkup(main_menu_keyboard()),
        )
    elif query.data == "info":
        await query.edit_message_text(
            "ℹ️ Это демонстрационный бот с расширенным функционалом.\n"
            "Версия: 2.0\n"
            "Разработчик: Ваше Имя",
            reply_markup=InlineKeyboardMarkup(main_menu_keyboard()),
        )
    elif query.data == "settings":
        await query.edit_message_text(
            "⚙️ Настройки бота:",
            reply_markup=InlineKeyboardMarkup(settings_menu_keyboard()),
        )
        return SUBMENU
    elif query.data == "help":
        await query.edit_message_text(
            "🆘 Доступные команды:\n"
            "/start - начать работу с ботом\n"
            "/menu - показать главное меню\n"
            "/cancel - отменить текущее действие\n\n"
            "Вы также можете использовать кнопки меню для навигации.",
            reply_markup=InlineKeyboardMarkup(main_menu_keyboard()),
        )
        return MENU
    elif query.data == "back_to_main":
        await query.edit_message_text(
            "Главное меню:",
            reply_markup=InlineKeyboardMarkup(main_menu_keyboard()),
        )
        return MENU
    elif query.data == "notifications":
        await query.edit_message_text(
            "🔔 Настройки уведомлений:\n"
            "Здесь можно настроить частоту и тип уведомлений.\n"
            "Функция в разработке.",
            reply_markup=InlineKeyboardMarkup(settings_menu_keyboard()),
        )
    elif query.data == "language":
        await query.edit_message_text(
            "🌍 Выбор языка:\n"
            "Доступные языки:\n"
            "- Русский\n"
            "- English\n"
            "Функция в разработке.",
            reply_markup=InlineKeyboardMarkup(settings_menu_keyboard()),
        )

# Обработчик команды /menu
async def show_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Главное меню:",
        reply_markup=InlineKeyboardMarkup(main_menu_keyboard()),
    )
    return MENU

# Обработчик текстовых сообщений
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text.lower()
    
    if text == "привет":
        await update.message.reply_text(
            "Привет! Как я могу вам помочь?",
            reply_markup=InlineKeyboardMarkup(main_menu_keyboard()),
        )
    elif text == "пока":
        await update.message.reply_text(
            "До свидания! Возвращайтесь скорее!",
            reply_markup=ReplyKeyboardRemove(),
        )
    else:
        await update.message.reply_text(
            "Я не понял ваше сообщение. Попробуйте выбрать действие из меню:",
            reply_markup=InlineKeyboardMarkup(main_menu_keyboard()),
        )

# Обработчик команды /cancel
async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Действие отменено.",
        reply_markup=InlineKeyboardMarkup(main_menu_keyboard()),
    )
    return MENU

# Обработчик ошибок
async def error(update: Update, context: ContextTypes.DEFAULT_TYPE):
    logger.warning(f'Update "{update}" caused error "{context.error}"')

def main():
    # Создаем Application
    application = Application.builder().token(BOT_TOKEN).build()

    # Настройка ConversationHandler
    conv_handler = ConversationHandler(
        entry_points=[CommandHandler("start", start)],
        states={
            MENU: [
                CallbackQueryHandler(button_click),
                CommandHandler("menu", show_menu),
                CommandHandler("cancel", cancel),
            ],
            SUBMENU: [
                CallbackQueryHandler(button_click),
                CommandHandler("menu", show_menu),
                CommandHandler("cancel", cancel),
            ],
        },
        fallbacks=[CommandHandler("cancel", cancel)],
    )

    # Добавляем обработчики
    application.add_handler(conv_handler)
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    application.add_error_handler(error)

    # Запускаем бота
    application.run_polling()

if __name__ == "__main__":
    main()