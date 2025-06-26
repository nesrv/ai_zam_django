import logging
import os
import signal
import sys
import asyncio
import uuid
import time
from datetime import datetime
from dotenv import load_dotenv
from openai import OpenAI
from telegram import Update, ReplyKeyboardMarkup, KeyboardButton
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes, ConversationHandler, JobQueue
import urllib.request
from http.server import HTTPServer, BaseHTTPRequestHandler
import threading

# Загружаем переменные окружения из файла .env
load_dotenv()

# Получаем токены из переменных окружения
TELEGRAM_TOKEN = os.environ['TELEGRAM_TOKEN']
DEEPSEEK_API_KEY = os.environ['DEEPSEEK_API_KEY']
DEEPSEEK_BASE_URL = "https://api.deepseek.com"

# Replit настройки
PORT = int(os.getenv('PORT', 8080))

# Генерируем уникальный ID сессии
SESSION_ID = str(uuid.uuid4())[:8]
BOT_START_TIME = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

logging.basicConfig(
    format=f'%(asctime)s - [{SESSION_ID}] - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

# Логируем запуск бота
logging.info(f"🚀 БОТ ЗАПУЩЕН! Session ID: {SESSION_ID}, Время запуска: {BOT_START_TIME}")

class HealthCheckHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path == '/health':
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            
            current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            uptime_seconds = int(time.time() - time.mktime(time.strptime(BOT_START_TIME, '%Y-%m-%d %H:%M:%S')))
            
            response = {
                "status": "ok",
                "session_id": SESSION_ID,
                "start_time": BOT_START_TIME,
                "current_time": current_time,
                "uptime_seconds": uptime_seconds,
                "active_timers": len([k for k, v in user_timers.items() if v == 'waiting'])
            }
            
            import json
            self.wfile.write(json.dumps(response).encode())
            logging.info(f"🏥 Health check запрос от {self.client_address[0]}")
        else:
            self.send_response(404)
            self.end_headers()
    
    def log_message(self, format, *args):
        # Отключаем стандартное логирование HTTP сервера
        pass

def start_health_server():
    """Запускаем HTTP сервер для health check"""
    server = HTTPServer(('0.0.0.0', PORT), HealthCheckHandler)
    logging.info(f"🏥 Health check сервер запущен на порту {PORT}")
    server.serve_forever()

def format_menu_text(text):
    """Заменяем символы на эмодзи"""
    # Заменяем различные символы на эмодзи
    text = text.replace('# ', '🍽️ ')
    text = text.replace('## ', '📅 ')
    text = text.replace('### ', '🍴 ')
    text = text.replace('- ', '• ')
    text = text.replace('* ', '• ')
    text = text.replace('МЕНЮ НА НЕДЕЛЮ', '🍽️ МЕНЮ НА НЕДЕЛЮ')
    text = text.replace('СПИСОК ПОКУПОК', '🛍️ СПИСОК ПОКУПОК')

    # Добавляем эмодзи к дням недели
    days = {
        'Понедельник': '📅 Понедельник',
        'Вторник': '📅 Вторник',
        'Среда': '📅 Среда',
        'Четверг': '📅 Четверг',
        'Пятница': '📅 Пятница',
        'Суббота': '📅 Суббота',
        'Воскресенье': '📅 Воскресенье'
    }

    for day, emoji_day in days.items():
        text = text.replace(f'{day}:', f'{emoji_day}:')

    # Добавляем эмодзи к приёмам пищи
    text = text.replace('Завтрак:', '🍳 Завтрак:')
    text = text.replace('Обед:', '🍲 Обед:')
    text = text.replace('Ужин:', '🍽️ Ужин:')

    # Добавляем пустые строки между приёмами пищи в меню на день
    if 'МЕНЮ НА ДЕНЬ' in text:
        # Добавляем пустые строки после завтрака и обеда
        import re
        # Находим строки с завтраком и обедом и добавляем пустую строку
        text = re.sub(r'(🍳 Завтрак:.*?)\n(?=🍲 Обед:)', r'\1\n\n', text)
        text = re.sub(r'(🍲 Обед:.*?)\n(?=🍽️ Ужин:)', r'\1\n\n', text)

    return text

def generate_weekly_menu(preferences):
    """Генерация меню на неделю"""
    try:
        logging.info("Подключаюсь к DeepSeek...")
        client = OpenAI(api_key=DEEPSEEK_API_KEY, base_url=DEEPSEEK_BASE_URL)

        prompt = f"""Ты опытный повар с 20-летним стажем. Составь меню на неделю (7 дней) для семьи из 4 человек, учитывая следующие предпочтения: {preferences}.

Меню должно быть разнообразным, полезным и вкусным и легко готовиться. Для каждого дня укажи:
1. Завтрак
2. Обед  
3. Ужин

После меню составь полный список покупок на всю неделю с указанием количества продуктов.

ВАЖНО: НЕ ИСПОЛЬЗУЙ символы # и * в ответе. Используй только тире (-) для списков.

Формат ответа:
МЕНЮ НА НЕДЕЛЮ:
Понедельник:
- Завтрак: [блюдо]
- Обед: [блюдо]
- Ужин: [блюдо]

[и так далее для всех дней]

СПИСОК ПОКУПОК:
- [продукт] - [количество]
- [продукт] - [количество]
[и так далее]"""

        return _generate_menu(client, prompt)

    except Exception as e:
        error_msg = f"Ошибка при работе с DeepSeek: {str(e)}"
        logging.error(error_msg)
        return error_msg

def generate_daily_menu(preferences):
    """Генерация меню на один день"""
    try:
        logging.info("Подключаюсь к DeepSeek...")
        client = OpenAI(api_key=DEEPSEEK_API_KEY, base_url=DEEPSEEK_BASE_URL)

        prompt = f"""Ты опытный повар с 20-летним стажем. Составь меню на один день для семьи из 4 человек, учитывая следующие предпочтения: {preferences}.

Меню должно быть полезным, вкусным и легко готовиться. Укажи:
1. Завтрак
2. Обед  
3. Ужин

После меню составь список покупок на этот день с указанием количества продуктов.

ВАЖНО: НЕ ИСПОЛЬЗУЙ символы # и * в ответе. Используй только тире (-) для списков.

Формат ответа:
МЕНЮ НА ДЕНЬ:
- Завтрак: [блюдо]
- Обед: [блюдо]
- Ужин: [блюдо]

СПИСОК ПОКУПОК:
- [продукт] - [количество]
- [продукт] - [количество]
[и так далее]"""

        return _generate_menu(client, prompt)

    except Exception as e:
        error_msg = f"Ошибка при работе с DeepSeek: {str(e)}"
        logging.error(error_msg)
        return error_msg

def _generate_menu(client, prompt):
    """Общая функция генерации меню"""

    logging.info("Отправляю запрос к DeepSeek...")

    # Пробуем разные модели
    models_to_try = ["deepseek-chat", "deepseek-coder"]

    for model in models_to_try:
        try:
            logging.info(f"Пробую модель: {model}")
            response = client.chat.completions.create(
                model=model,
                messages=[
                    {"role": "system", "content": "Ты опытный повар с 20-летним стажем."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7,
                max_tokens=2000
            )
            break
        except Exception as model_error:
            logging.warning(f"Модель {model} недоступна: {model_error}")
            if model == models_to_try[-1]:  # Последняя модель
                raise model_error
            continue

    menu_content = response.choices[0].message.content
    logging.info(f"Меню сгенерировано, длина: {len(menu_content)} символов")
    return menu_content

# Словарь для отслеживания автогенерации
user_timers = {}

async def auto_generate_menu(chat_id, menu_type, bot):
    """Автоматическая генерация меню через 60 секунд"""
    await asyncio.sleep(60)  # Ждем 60 секунд

    # Проверяем, не ответил ли пользователь
    if chat_id not in user_timers or user_timers[chat_id] != 'waiting':
        return

    logging.info(f"Автогенерация меню для chat_id {chat_id}")

    keyboard = [
        [KeyboardButton("📅 Неделя"), KeyboardButton("🍽️ Сегодня")]
    ]
    reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True, one_time_keyboard=False)

    await bot.send_message(
        chat_id=chat_id,
        text="Я понял, сейчас всё сделаю! Генерирую меню на свое усмотрение...",
        reply_markup=reply_markup
    )

    try:
        preferences = "сбалансированное питание"

        if menu_type == "🍽️ Сегодня":
            menu_text = generate_daily_menu(preferences)
        else:
            menu_text = generate_weekly_menu(preferences)

        formatted_menu = format_menu_text(menu_text)

        if len(formatted_menu) > 4096:
            parts = [formatted_menu[i:i+4096] for i in range(0, len(formatted_menu), 4096)]
            for i, part in enumerate(parts):
                if i == len(parts) - 1:
                    await bot.send_message(chat_id=chat_id, text=f"Часть {i+1}:\n{part}", reply_markup=reply_markup)
                else:
                    await bot.send_message(chat_id=chat_id, text=f"Часть {i+1}:\n{part}")
        else:
            await bot.send_message(chat_id=chat_id, text=formatted_menu, reply_markup=reply_markup)

    except Exception as e:
        logging.error(f"Ошибка автогенерации: {e}")
        await bot.send_message(
            chat_id=chat_id,
            text="Ошибка генерации меню",
            reply_markup=reply_markup
        )

    # Очищаем таймер
    if chat_id in user_timers:
        del user_timers[chat_id]



async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [KeyboardButton("📅 Неделя"), KeyboardButton("🍽️ Сегодня")]
    ]
    reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True, one_time_keyboard=False)

    # Логируем обращение пользователя
    logging.info(f"👤 Пользователь {update.effective_user.first_name} (ID: {update.effective_chat.id}) запустил команду /start")

    await update.message.reply_text(
        '👨‍🍳 Здравствуйте! Я ваш помощник-повар.\n\n'
        '🍽️ Помогу составить меню и список покупок.\n\n'
        '✍️ Напишите ваши предпочтения в питании (например: "без мяса", "люблю рыбу", "нет ограничений") и нажмите кнопку!\n\n'
        '🔧 Команды:\n'
        '/command1 - Меню на сегодня\n'
        '/command2 - Меню на неделю\n\n'
        f'🔢 Session ID: {SESSION_ID}\n'
        f'⏰ Запущен: {BOT_START_TIME}',
        reply_markup=reply_markup
    )

async def command1(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Команда для меню на сегодня"""
    keyboard = [
        [KeyboardButton("📅 Неделя"), KeyboardButton("🍽️ Сегодня")]
    ]
    reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True, one_time_keyboard=False)
    
    await update.message.reply_text(
        "Напишите ваши предпочтения в питании для меню на сегодня.\n\n"
        "💡 Если у вас нет особых предпочтений, подождите 1 минуту - и я сформирую меню на свое усмотрение!",
        reply_markup=reply_markup
    )
    context.user_data['menu_type'] = "🍽️ Сегодня"
    
    # Запускаем таймер автогенерации
    chat_id = update.effective_chat.id
    user_timers[chat_id] = 'waiting'
    asyncio.create_task(auto_generate_menu(chat_id, "🍽️ Сегодня", context.bot))
    logging.info(f"Запущен таймер автогенерации для пользователя {chat_id} (команда /command1)")

async def command2(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Команда для меню на неделю"""
    keyboard = [
        [KeyboardButton("📅 Неделя"), KeyboardButton("🍽️ Сегодня")]
    ]
    reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True, one_time_keyboard=False)
    
    await update.message.reply_text(
        "Напишите ваши предпочтения в питании для меню на неделю.\n\n"
        "💡 Если у вас нет особых предпочтений, подождите 1 минуту - и я сформирую меню на свое усмотрение!",
        reply_markup=reply_markup
    )
    context.user_data['menu_type'] = "📅 Неделя"
    
    # Запускаем таймер автогенерации
    chat_id = update.effective_chat.id
    user_timers[chat_id] = 'waiting'
    asyncio.create_task(auto_generate_menu(chat_id, "📅 Неделя", context.bot))
    logging.info(f"Запущен таймер автогенерации для пользователя {chat_id} (команда /command2)")

async def status(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Команда для проверки статуса бота"""
    current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    uptime_seconds = int(time.time() - time.mktime(time.strptime(BOT_START_TIME, '%Y-%m-%d %H:%M:%S')))
    uptime_minutes = uptime_seconds // 60
    uptime_hours = uptime_minutes // 60
    uptime_days = uptime_hours // 24
    
    uptime_str = f"{uptime_days}д {uptime_hours%24}ч {uptime_minutes%60}м {uptime_seconds%60}с"
    
    active_timers = len([k for k, v in user_timers.items() if v == 'waiting'])
    
    status_text = (
        f"🤖 **Статус бота**:\n\n"
        f"🔢 Session ID: `{SESSION_ID}`\n"
        f"⏰ Запущен: `{BOT_START_TIME}`\n"
        f"📅 Текущее время: `{current_time}`\n"
        f"⏱️ Время работы: `{uptime_str}`\n"
        f"👥 Активных таймеров: `{active_timers}`\n"
        f"💾 Пользователей в памяти: `{len(user_timers)}`"
    )
    
    logging.info(f"📊 Запрошен статус бота пользователем {update.effective_chat.id}")
    await update.message.reply_text(status_text, parse_mode='Markdown')

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):

    message_text = update.message.text
    chat_id = update.effective_chat.id

    keyboard = [
        [KeyboardButton("📅 Неделя"), KeyboardButton("🍽️ Сегодня")]
    ]
    reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True, one_time_keyboard=False)

    # Проверяем, нажата ли кнопка
    if message_text in ["📅 Неделя", "🍽️ Сегодня"]:
        await update.message.reply_text(
            "Напишите ваши предпочтения в питании.\n\n"
            "💡 Если у вас нет особых предпочтений, подождите 1 минуту - и я сформирую меню на свое усмотрение!",
            reply_markup=reply_markup
        )
        context.user_data['menu_type'] = message_text

        # Запускаем таймер автогенерации
        user_timers[chat_id] = 'waiting'
        asyncio.create_task(auto_generate_menu(chat_id, message_text, context.bot))
        logging.info(f"Запущен таймер автогенерации для chat_id {chat_id}")
        return

    # Получаем предпочтения и генерируем меню
    preferences = message_text.lower()
    menu_type = context.user_data.get('menu_type', '📅 Неделя')

    # Отменяем автогенерацию, так как пользователь ответил
    if chat_id in user_timers:
        user_timers[chat_id] = 'answered'
        logging.info(f"Пользователь ответил, отменяем автогенерацию для chat_id {chat_id}")



    if menu_type == "🍽️ Сегодня":
        await update.message.reply_text("Генерирую меню на сегодня...", reply_markup=reply_markup)
        menu_text = generate_daily_menu(preferences)
    else:
        await update.message.reply_text("Генерирую меню на неделю...", reply_markup=reply_markup)
        menu_text = generate_weekly_menu(preferences)

    try:
        # Форматируем текст с эмодзи
        formatted_menu = format_menu_text(menu_text)

        # Отправляем меню
        if len(formatted_menu) > 4096:
            parts = [formatted_menu[i:i+4096] for i in range(0, len(formatted_menu), 4096)]
            for i, part in enumerate(parts):
                if i == len(parts) - 1:
                    await update.message.reply_text(f"Часть {i+1}:\n{part}", reply_markup=reply_markup)
                else:
                    await update.message.reply_text(f"Часть {i+1}:\n{part}")
        else:
            await update.message.reply_text(formatted_menu, reply_markup=reply_markup)

    except Exception as e:
        logging.error(f"Ошибка: {e}")
        await update.message.reply_text("Ошибка генерации меню", reply_markup=reply_markup)

def signal_handler(signum, frame):
    """Обработчик сигналов для корректного завершения"""
    print("\nПолучен сигнал завершения. Останавливаю бота...")
    sys.exit(0)

def main():
    if not TELEGRAM_TOKEN:
        print("ОШИБКА: TELEGRAM_TOKEN не найден в переменных окружения!")
        sys.exit(1)

    if not DEEPSEEK_API_KEY:
        print("ОШИБКА: DEEPSEEK_API_KEY не найден в переменных окружения!")
        sys.exit(1)

    print(f"🚀 Запускаю бота на Replit...")
    print(f"📅 Время запуска: {BOT_START_TIME}")
    print(f"🔢 Session ID: {SESSION_ID}")
    print(f"🔑 Telegram Token: {TELEGRAM_TOKEN[:20] if TELEGRAM_TOKEN else 'НЕ УСТАНОВЛЕН'}...")
    print(f"🔑 DeepSeek API Key: {'Установлен' if DEEPSEEK_API_KEY else 'НЕ УСТАНОВЛЕН'}")

    # Создаем приложение
    app = ApplicationBuilder().token(TELEGRAM_TOKEN).build()

    # Обработчики
    app.add_handler(CommandHandler('start', start))
    app.add_handler(CommandHandler('command1', command1))
    app.add_handler(CommandHandler('command2', command2))
    app.add_handler(CommandHandler('status', status))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    # Запускаем HTTP сервер в отдельном потоке
    health_thread = threading.Thread(target=start_health_server, daemon=True)
    health_thread.start()
    
    # Запуск в polling режиме для Replit
    print("🔄 Запускаю в polling режиме")
    logging.info(f"🔄 Polling запущен. Session ID: {SESSION_ID}")
    app.run_polling(drop_pending_updates=True)

if __name__ == '__main__':
    # Регистрируем обработчики сигналов
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)

    try:
        main()
    except KeyboardInterrupt:
        print("\nБот остановлен пользователем.")
    except Exception as e:
        print(f"Ошибка запуска бота: {e}")
        sys.exit(1)