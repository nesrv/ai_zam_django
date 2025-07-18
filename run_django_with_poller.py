#!/usr/bin/env python
"""
Скрипт для запуска Django с поллером Telegram в одном процессе
"""
import os
import sys
import django
import logging
import threading
import time
from dotenv import load_dotenv

# Настройка путей для Django
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ai_zam.settings')

# Инициализация Django
django.setup()

# Загрузка переменных окружения
load_dotenv()

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('django_with_poller.log')
    ]
)
logger = logging.getLogger(__name__)

def start_telegram_poller():
    """Запуск поллера Telegram в отдельном потоке"""
    try:
        logger.info("Запуск поллера Telegram...")
        
        # Проверяем, запущен ли уже другой экземпляр поллера
        from telegrambot.telegram_poller import is_another_instance_running
        if is_another_instance_running():
            logger.warning("Обнаружен другой запущенный экземпляр поллера. Новый экземпляр не будет запущен.")
            return
        
        # Запускаем поллер
        from telegrambot.telegram_poller import start_polling
        success = start_polling()
        
        if success:
            logger.info("Поллер Telegram успешно запущен")
        else:
            logger.error("Не удалось запустить поллер Telegram")
    except Exception as e:
        logger.error(f"Ошибка при запуске поллера Telegram: {e}")

def start_django_server():
    """Запуск Django сервера"""
    try:
        logger.info("Запуск Django сервера...")
        
        # Запускаем Django сервер
        from django.core.management import call_command
        call_command('runserver', '0.0.0.0:8000')
    except Exception as e:
        logger.error(f"Ошибка при запуске Django сервера: {e}")

def main():
    """Основная функция скрипта"""
    logger.info("Запуск Django с поллером Telegram...")
    
    # Запускаем поллер в отдельном потоке
    poller_thread = threading.Thread(target=start_telegram_poller, daemon=True)
    poller_thread.start()
    logger.info("Поток поллера Telegram запущен")
    
    # Запускаем Django сервер в основном потоке
    start_django_server()

if __name__ == "__main__":
    main()