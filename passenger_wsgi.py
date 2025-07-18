import os
import sys
import threading
import logging
import pathlib

# Явная загрузка переменных окружения из .env
try:
    from dotenv import load_dotenv
    # Получаем путь к корневой папке проекта
    BASE_DIR = pathlib.Path(__file__).resolve().parent
    ENV_FILE = BASE_DIR / '.env'
    
    # Загружаем переменные окружения
    load_dotenv(ENV_FILE)
    
    # Явно устанавливаем токен бота, если он не был загружен
    if not os.getenv('TELEGRAM_TOKEN'):
        # Замените на ваш токен
        os.environ['TELEGRAM_TOKEN'] = '7836693206:AAFgvbLhQSuDCCWPr5zaafDn0W_-CGF0yGk'
        os.environ['TELEGRAM_POLL_INTERVAL'] = '20'
        
    logger = logging.getLogger(__name__)
    logger.info(f"TELEGRAM_TOKEN: {os.getenv('TELEGRAM_TOKEN')[:10]}...")
except Exception as e:
    print(f"[Ошибка загрузки .env]: {e}")

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('passenger_telegram_poller.log')
    ]
)
logger = logging.getLogger(__name__)

# Добавляем путь к проекту
sys.path.insert(0, os.path.dirname(__file__))

# Импортируем WSGI-приложение Django
try:
    from ai_zam.wsgi import application
    logger.info("Django WSGI application успешно импортирован")
except Exception as e:
    logger.error(f"Ошибка импорта Django WSGI application: {e}")
    raise

# Запускаем поллер в отдельном потоке
def start_telegram_poller():
    try:
        logger.info("Запуск поллера Telegram из Passenger...")
        
        # Принудительно удаляем файл блокировки, если он существует
        from telegrambot.telegram_poller import remove_lock_file
        
        logger.info("Удаляем файл блокировки")
        remove_lock_file()
        logger.info("Файл блокировки удален")
        
        # Запускаем поллер
        from telegrambot.telegram_poller import start_polling
        success = start_polling()
        
        if success:
            logger.info("Поллер Telegram успешно запущен из Passenger")
        else:
            logger.error("Не удалось запустить поллер Telegram из Passenger")
    except Exception as e:
        logger.error(f"Ошибка при запуске поллера Telegram из Passenger: {e}")

# Запускаем поллер в отдельном потоке
try:
    poller_thread = threading.Thread(target=start_telegram_poller, daemon=True)
    poller_thread.start()
    logger.info("Поток поллера Telegram запущен из Passenger")
except Exception as e:
    logger.error(f"Ошибка создания потока для поллера: {e}")