from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes

# Токен бота (замените на ваш)
TOKEN = "7836693206:AAE_wRnOiWm0xhRlP7cr8Q0AvaPEgZCgTFw"
# Имя бота (для удобства)
BOT_USERNAME = "@NeSrv2Bot"  # Замените на ваш username

MAIN_MENU = [
    ["🍳 Меню на день", "📅 Меню на неделю"],
    ["💬 Общий чат", "📋 Генерация документов"],
    ["❓ Помощь"]
]

DOCUMENT_BUTTONS = [
    ["📄 ЛЗК", "📊 ВОР"],
    ["📋 ТЗ", "❓ Опросный лист"],
    ["🔍 Акт скрытых работ", "📝 Пояснительная записка"],
    ["🔙 Назад в меню"]
]

# Обработчик команды /start
async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Привет! Я тестовый бот. Напиши что-нибудь!",
        reply_markup=ReplyKeyboardMarkup(MAIN_MENU, resize_keyboard=True)
    )

# Обработчик команды /help
async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("""
    Доступные команды:
    /start - начать общение
    /help - помощь
    """,
    reply_markup=ReplyKeyboardMarkup(MAIN_MENU, resize_keyboard=True)
    )

# Обработчик обычных текстовых сообщений
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text
    user_message = text.lower()

    if text == "📋 Генерация документов":
        await update.message.reply_text(
            "Выберите тип документа для генерации:",
            reply_markup=ReplyKeyboardMarkup(DOCUMENT_BUTTONS, resize_keyboard=True)
        )
        return
    elif text in sum(DOCUMENT_BUTTONS, []):
        doc_map = {
            "📄 ЛЗК": "лимитно-заборную карту (ЛЗК)",
            "📊 ВОР": "ведомость объемов работ (ВОР)",
            "📋 ТЗ": "техническое задание (ТЗ)",
            "❓ Опросный лист": "опросный лист для подрядчика",
            "🔍 Акт скрытых работ": "акт скрытых работ",
            "📝 Пояснительная записка": "пояснительную записку к проекту"
        }
        doc_name = doc_map.get(text, "документ")
        await update.message.reply_text(
            f"Пожалуйста, укажите параметры для генерации {doc_name}.\n\n"
            "💡 Пример: ...",
            reply_markup=ReplyKeyboardMarkup(DOCUMENT_BUTTONS, resize_keyboard=True)
        )
        return
    elif text == "🔙 Назад в меню":
        await update.message.reply_text(
            "Главное меню:",
            reply_markup=ReplyKeyboardMarkup(MAIN_MENU, resize_keyboard=True)
        )
        return
    elif "привет" in user_message:
        response = "Привет! Как дела?"
    elif "пока" in user_message:
        response = "До свидания! Возвращайся :)"
    else:
        response = "Я не понял сообщение. Попробуй /help"
    await update.message.reply_text(response, reply_markup=ReplyKeyboardMarkup(MAIN_MENU, resize_keyboard=True))

# Обработчик ошибок
async def error(update: Update, context: ContextTypes.DEFAULT_TYPE):
    print(f"Update {update} caused error {context.error}")

if __name__ == "__main__":
    print("Бот запускается...")
    app = Application.builder().token(TOKEN).build()

    # Регистрация обработчиков команд
    app.add_handler(CommandHandler("start", start_command))
    app.add_handler(CommandHandler("help", help_command))

    # Регистрация обработчика текстовых сообщений
    app.add_handler(MessageHandler(filters.TEXT, handle_message))

    # Регистрация обработчика ошибок
    app.add_error_handler(error)

    print("Бот работает...")
    app.run_polling(poll_interval=3)