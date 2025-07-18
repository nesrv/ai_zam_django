"""
WSGI config for ai_zam project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/5.2/howto/deployment/wsgi/
"""

import os
import threading
import logging
import pathlib

# Явная загрузка переменных окружения из .env
try:
    from dotenv import load_dotenv
    # Получаем путь к корневой папке проекта
    BASE_DIR = pathlib.Path(__file__).resolve().parent.parent
    ENV_FILE = BASE_DIR / '.env'
    
    # Загружаем переменные окружения
    load_dotenv(ENV_FILE)
    
    # Явно устанавливаем токен бота, если он не был загружен
    if not os.getenv('TELEGRAM_TOKEN'):
        # Замените на ваш токен
        os.environ['TELEGRAM_TOKEN'] = '7836693206:AAFgvbLhQSuDCCWPr5zaafDn0W_-CGF0yGk'
        os.environ['TELEGRAM_POLL_INTERVAL'] = '20'
except Exception as e:
    print(f"[Ошибка загрузки .env]: {e}")

from django.core.wsgi import get_wsgi_application

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('telegram_poller_wsgi.log')
    ]
)
logger = logging.getLogger(__name__)

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ai_zam.settings')

application = get_wsgi_application()

# Запускаем поллер Telegram в отдельном потоке
def start_telegram_poller():
    try:
        logger.info("Запуск поллера Telegram из WSGI...")
        
        # Проверяем, запущен ли уже другой экземпляр поллера
        from telegrambot.telegram_poller import is_another_instance_running
        if is_another_instance_running():
            logger.warning("Обнаружен другой запущенный экземпляр поллера. Новый экземпляр не будет запущен.")
            return
        
        # Запускаем поллер
        from telegrambot.telegram_poller import start_polling
        success = start_polling()
        
        if success:
            logger.info("Поллер Telegram успешно запущен из WSGI")
        else:
            logger.error("Не удалось запустить поллер Telegram из WSGI")
    except Exception as e:
        logger.error(f"Ошибка при запуске поллера Telegram из WSGI: {e}")

# Отключаем автоматический запуск поллера в WSGI, чтобы избежать конфликтов
# Для получения сообщений используйте отдельный скрипт: python run_telegram_poller.py
logger.info("Автоматический запуск поллера в WSGI отключен для предотвращения конфликтов")
