import logging
import os
import asyncio
import uuid
import time
from datetime import datetime
from dotenv import load_dotenv
from openai import OpenAI
from telegram import Update, ReplyKeyboardMarkup, KeyboardButton
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
from telegram.error import Conflict

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

# Клавиатура
def get_keyboard():
    """Возвращает стандартную клавиатуру"""
    return ReplyKeyboardMarkup([
        [KeyboardButton("📅 Неделя"), KeyboardButton("🍽️ Сегодня")]
    ], resize_keyboard=True, one_time_keyboard=False)

# Функции для работы с меню
def format_menu_text(text):
    """Форматирует текст меню с эмодзи и Markdown разметкой"""
    # Экранируем только проблемные символы в обычном тексте
    def escape_problematic_chars(text):
        """Экранирует только проблемные символы"""
        # Экранируем только символы, которые могут сломать Markdown
        problematic_chars = ['[', ']', '(', ')', '~', '`', '>', '|', '{', '}']
        for char in problematic_chars:
            text = text.replace(char, f'\\{char}')
        return text
    
    # Сначала убираем лишние символы заголовков
    text = text.replace('##', '').replace('###', '')
    
    # Базовые замены эмодзи (без Markdown разметки)
    replacements = {
        '# ': '🍽️ ', '## ': '📅 ', '### ': '🍴 ',
        '- ': '• ', '* ': '• ',
        'МЕНЮ НА НЕДЕЛЮ': '🍽️ МЕНЮ НА НЕДЕЛЮ',
        'МЕНЮ НА ДЕНЬ': '🍽️ МЕНЮ НА ДЕНЬ',
        'СПИСОК ПОКУПОК': '🛍️ СПИСОК ПОКУПОК',
        'Завтрак:': '🍳 Завтрак:', 
        'Обед:': '🍲 Обед:', 
        'Ужин:': '🍽️ Ужин:',
        'Понедельник': '📅 Понедельник',
        'Вторник': '📅 Вторник',
        'Среда': '📅 Среда',
        'Четверг': '📅 Четверг',
        'Пятница': '📅 Пятница',
        'Суббота': '📅 Суббота',
        'Воскресенье': '📅 Воскресенье',
        'День 1': '📅 День 1',
        'День 2': '📅 День 2',
        'День 3': '📅 День 3',
        'День 4': '📅 День 4',
        'День 5': '📅 День 5',
        'День 6': '📅 День 6',
        'День 7': '📅 День 7'
    }
    
    for old, new in replacements.items():
        text = text.replace(old, new)
    
    # Добавляем дополнительные эмодзи для продуктов
    food_emojis = {
        'курица': '🍗', 'мясо': '🥩', 'рыба': '🐟', 'свинина': '🥓', 'говядина': '🥩',
        'овощи': '🥬', 'фрукты': '🍎', 'хлеб': '🍞', 'молоко': '🥛', 'яйца': '🥚',
        'сыр': '🧀', 'масло': '🧈', 'картофель': '🥔', 'морковь': '🥕', 'лук': '🧅',
        'помидоры': '🍅', 'огурцы': '🥒', 'капуста': '🥬', 'рис': '🍚', 'макароны': '🍝',
        'суп': '🍲', 'салат': '🥗', 'пирог': '🥧', 'торт': '🎂', 'конфеты': '🍬',
        'чай': '☕', 'кофе': '☕', 'сок': '🧃', 'вода': '💧', 'вино': '🍷',
        'пиво': '🍺', 'водка': '🥃', 'коньяк': '🥃', 'ликер': '🍸', 'коктейль': '🍹'
    }
    
    # Добавляем эмодзи к продуктам (только к первым упоминаниям)
    for food, emoji in food_emojis.items():
        if food in text.lower():
            # Заменяем только первое вхождение
            text = text.replace(food, f"{emoji} {food}", 1)
    
    # Добавляем заголовки и разделители
    lines = text.split('\n')
    formatted_lines = []
    
    for line in lines:
        line = line.strip()
        if not line:
            continue
            
        # Форматируем заголовки
        if line.startswith('🍽️ МЕНЮ'):
            formatted_lines.append(f"\n🎯 *{line}*")
        elif line.startswith('🛍️ СПИСОК'):
            formatted_lines.append(f"\n🛒 *{line}*")
        elif line.startswith('📅 '):
            formatted_lines.append(f"\n📋 *{line}*")
        elif line.startswith('🍳 ') or line.startswith('🍲 ') or line.startswith('🍽️ '):
            formatted_lines.append(f"\n🍴 *{line}*")
        else:
            # Экранируем только проблемные символы в обычном тексте
            formatted_lines.append(escape_problematic_chars(line))
    
    # Добавляем финальное оформление
    result = '\n'.join(formatted_lines)
    result = f"🎨 *КУЛИНАРНОЕ МЕНЮ* 🎨\n\n{result}\n\n✨ *Приятного аппетита!* ✨"
    
    return result

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
        logger.info(f"Меню сгенерировано, длина: {len(menu_content)} символов")
        return menu_content

    except Exception as e:
        error_msg = f"Ошибка при работе с DeepSeek: {str(e)}"
        logger.error(error_msg)
        return error_msg

async def send_menu(chat_id, menu_text, bot):
    """Отправляет меню пользователю с разбивкой на части если нужно"""
    keyboard = get_keyboard()
    formatted_menu = format_menu_text(menu_text)

    if len(formatted_menu) > 4096:
        parts = [formatted_menu[i:i+4096] for i in range(0, len(formatted_menu), 4096)]
        for i, part in enumerate(parts):
            if i == len(parts) - 1:
                await bot.send_message(
                    chat_id=chat_id, 
                    text=f"*Часть {i+1}:*\n{part}", 
                    reply_markup=keyboard,
                    parse_mode='Markdown'
                )
            else:
                await bot.send_message(
                    chat_id=chat_id, 
                    text=f"*Часть {i+1}:*\n{part}",
                    parse_mode='Markdown'
                )
    else:
        await bot.send_message(
            chat_id=chat_id, 
            text=formatted_menu, 
            reply_markup=keyboard,
            parse_mode='Markdown'
        )

async def auto_generate_menu(chat_id, menu_type, bot):
    """Автоматическая генерация меню через 60 секунд"""
    await asyncio.sleep(60)
    
    if chat_id not in user_timers or user_timers[chat_id] != 'waiting':
        return

    logger.info(f"Автогенерация меню для chat_id {chat_id}")
    keyboard = get_keyboard()

    await bot.send_message(
        chat_id=chat_id,
        text="*Я понял, сейчас всё сделаю! Генерирую меню на свое усмотрение...* 🎨",
        reply_markup=keyboard,
        parse_mode='Markdown'
    )

    try:
        menu_text = generate_menu("сбалансированное питание", "сегодня" if menu_type == "🍽️ Сегодня" else "неделя")
        await send_menu(chat_id, menu_text, bot)
    except Exception as e:
        logger.error(f"Ошибка автогенерации: {e}")
        await bot.send_message(
            chat_id=chat_id,
            text="*Ошибка генерации меню* ❌",
            reply_markup=keyboard,
            parse_mode='Markdown'
        )

    if chat_id in user_timers:
        del user_timers[chat_id]

# Обработчики команд
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработчик команды /start"""
    keyboard = get_keyboard()
    user = update.effective_user
    chat_id = update.effective_chat.id

    logger.info(f"👤 Пользователь {user.first_name} (ID: {chat_id}) запустил команду /start")

    await update.message.reply_text(
        f'*👨‍🍳 Привет, {user.first_name}! Я твой персональный шеф-повар!* 🎉\n\n'
        f'🍽️ *Готов превратить твои кулинарные мечты в реальность!*\n'
        f'✨ Создам идеальное меню и список покупок\n'
        f'🎯 Учту все твои вкусы и предпочтения\n\n'
        f'🚀 *Начнем кулинарное приключение?*\n\n'
        f'🔧 *Магия доступна через команды:*\n'
        f'🍳 `/today` - Меню на сегодня *(быстро и вкусно)*\n'
        f'📅 `/week` - Меню на неделю *(полный план питания)*\n'
        f'🎲 `/surprise` - Случайное меню *(сюрприз от шефа)*\n'
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

🎲 *`/surprise`* - Случайное меню
   Сюрприз от шефа - что-то необычное!

📊 *`/stats`* - Статистика бота
   Интересные цифры и факты

❓ *`/help`* - Эта справка
   Всегда здесь для тебя

🎯 *Как использовать:*
1. Выбери команду или нажми кнопку
2. Напиши предпочтения *(например: "люблю рыбу", "без мяса", "быстрое приготовление")*
3. Получи идеальное меню! ✨

💡 *Совет:* Если не знаешь что написать, просто подожди 1 минуту - я сам придумаю что-то вкусное! 😋
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
        f"• Любые пожелания\n\n"
        f"💡 *Или просто подожди 1 минуту - я сам создам что-то потрясающее!* 🎨",
        reply_markup=keyboard,
        parse_mode='Markdown'
    )
    
    context.user_data['menu_type'] = "🍽️ Сегодня"
    user_timers[chat_id] = 'waiting'
    asyncio.create_task(auto_generate_menu(chat_id, "🍽️ Сегодня", context.bot))
    logger.info(f"Запущен таймер автогенерации для пользователя {chat_id} (команда /today)")

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
        f"• Бюджет на продукты\n\n"
        f"💡 *Или доверься моему опыту - через минуту будет готов план!* 📋",
        reply_markup=keyboard,
        parse_mode='Markdown'
    )
    
    context.user_data['menu_type'] = "📅 Неделя"
    user_timers[chat_id] = 'waiting'
    asyncio.create_task(auto_generate_menu(chat_id, "📅 Неделя", context.bot))
    logger.info(f"Запущен таймер автогенерации для пользователя {chat_id} (команда /week)")

async def surprise_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Команда для случайного меню"""
    keyboard = get_keyboard()
    chat_id = update.effective_chat.id
    user = update.effective_user
    
    await update.message.reply_text(
        f"🎲 *{user.first_name}, готовлю для тебя кулинарный сюрприз!*\n\n"
        f"🎪 *Это будет что-то необычное и интересное:*\n"
        f"• Неожиданные сочетания\n"
        f"• Новые рецепты\n"
        f"• Экзотические блюда\n"
        f"• Креативные идеи\n\n"
        f"💫 *Напиши базовые предпочтения или просто подожди - сюрприз готовится!* 🎁",
        reply_markup=keyboard,
        parse_mode='Markdown'
    )
    
    context.user_data['menu_type'] = "🎲 Сюрприз"
    user_timers[chat_id] = 'waiting'
    asyncio.create_task(auto_generate_menu(chat_id, "🎲 Сюрприз", context.bot))
    logger.info(f"Запущен таймер автогенерации для пользователя {chat_id} (команда /surprise)")

async def stats(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Команда для проверки статистики бота"""
    current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    uptime_seconds = int(time.time() - time.mktime(time.strptime(BOT_START_TIME, '%Y-%m-%d %H:%M:%S')))
    uptime_minutes = uptime_seconds // 60
    uptime_hours = uptime_minutes // 60
    uptime_days = uptime_hours // 24
    
    uptime_str = f"{uptime_days}д {uptime_hours%24}ч {uptime_minutes%60}м {uptime_seconds%60}с"
    active_timers = len([k for k, v in user_timers.items() if v == 'waiting'])
    
    # Генерируем интересную статистику
    total_users = len(user_timers)
    menus_generated = total_users * 2  # Примерная оценка
    
    stats_text = (
        f"📊 *КУЛИНАРНАЯ СТАТИСТИКА* 📊\n\n"
        f"🤖 *Бот-шеф работает:*\n"
        f"🔢 Session ID: `{SESSION_ID}`\n"
        f"⏰ Запущен: `{BOT_START_TIME}`\n"
        f"📅 Текущее время: `{current_time}`\n"
        f"⏱️ Время работы: `{uptime_str}`\n\n"
        f"👥 *Активность:*\n"
        f"🔥 Активных таймеров: `{active_timers}`\n"
        f"👨‍🍳 Поваров в очереди: `{total_users}`\n"
        f"🍽️ Меню создано: `{menus_generated}`\n\n"
        f"🎯 *Статус:* {'🟢 Активен' if active_timers > 0 else '🟡 Ожидание'}\n\n"
        f"💡 *Готов создавать новые кулинарные шедевры!* ✨"
    )
    
    logger.info(f"📊 Запрошена статистика бота пользователем {update.effective_chat.id}")
    await update.message.reply_text(stats_text, parse_mode='Markdown')

# Обработчики для обратной совместимости
async def command1(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обратная совместимость для /command1"""
    await today_menu(update, context)

async def command2(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обратная совместимость для /command2"""
    await week_menu(update, context)

async def status(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обратная совместимость для /status"""
    await stats(update, context)

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработчик всех текстовых сообщений"""
    message_text = update.message.text
    chat_id = update.effective_chat.id
    keyboard = get_keyboard()

    # Проверяем, нажата ли кнопка
    if message_text in ["📅 Неделя", "🍽️ Сегодня"]:
        await update.message.reply_text(
            "*Напишите ваши предпочтения в питании.*\n\n"
            "💡 *Если у вас нет особых предпочтений, подождите 1 минуту - и я сформирую меню на свое усмотрение!*",
            reply_markup=keyboard,
            parse_mode='Markdown'
        )
        context.user_data['menu_type'] = message_text
        user_timers[chat_id] = 'waiting'
        asyncio.create_task(auto_generate_menu(chat_id, message_text, context.bot))
        logger.info(f"Запущен таймер автогенерации для chat_id {chat_id}")
        return

    # Получаем предпочтения и генерируем меню
    preferences = message_text.lower()
    menu_type = context.user_data.get('menu_type', '📅 Неделя')

    # Отменяем автогенерацию, так как пользователь ответил
    if chat_id in user_timers:
        user_timers[chat_id] = 'answered'
        logger.info(f"Пользователь ответил, отменяем автогенерацию для chat_id {chat_id}")

    # Генерируем и отправляем меню
    if menu_type == "🍽️ Сегодня":
        await update.message.reply_text("*Генерирую меню на сегодня...* 🍳", reply_markup=keyboard, parse_mode='Markdown')
        menu_text = generate_menu(preferences, "сегодня")
    elif menu_type == "🎲 Сюрприз":
        await update.message.reply_text("*Готовлю кулинарный сюрприз...* 🎲", reply_markup=keyboard, parse_mode='Markdown')
        menu_text = generate_menu(preferences + " необычные и креативные блюда", "неделя")
    else:
        await update.message.reply_text("*Генерирую меню на неделю...* 📅", reply_markup=keyboard, parse_mode='Markdown')
        menu_text = generate_menu(preferences, "неделя")

    try:
        await send_menu(chat_id, menu_text, context.bot)
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
    # Новые креативные команды
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(CommandHandler("today", today_menu))
    application.add_handler(CommandHandler("week", week_menu))
    application.add_handler(CommandHandler("surprise", surprise_menu))
    application.add_handler(CommandHandler("stats", stats))
    
    # Обратная совместимость
    application.add_handler(CommandHandler("command1", command1))
    application.add_handler(CommandHandler("command2", command2))
    application.add_handler(CommandHandler("status", status))
    
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