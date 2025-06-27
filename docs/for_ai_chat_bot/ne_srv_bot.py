from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes

# Токен бота (замените на ваш)
TOKEN = "7836693206:AAE_wRnOiWm0xhRlP7cr8Q0AvaPEgZCgTFw"
# Имя бота (для удобства)
BOT_USERNAME = "@NeSrv2Bot"  # Замените на ваш username

# Обработчик команды /start
async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Привет! Я тестовый бот. Напиши что-нибудь!")

# Обработчик команды /help
async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("""
    Доступные команды:
    /start - начать общение
    /help - помощь
    """)

# Обработчик обычных текстовых сообщений
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_message = update.message.text.lower()
    
    if "привет" in user_message:
        response = "Привет! Как дела?"
    elif "пока" in user_message:
        response = "До свидания! Возвращайся :)"
    else:
        response = "Я не понял сообщение. Попробуй /help"
    
    await update.message.reply_text(response)

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