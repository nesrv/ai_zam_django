#!/usr/bin/env python
"""
Скрипт для запуска поллера Telegram отдельно от Django
"""
import os
import sys
import django
import time
import logging
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
        logging.FileHandler('telegram_poller.log')
    ]
)
logger = logging.getLogger(__name__)

# Импорт поллера
from telegrambot.telegram_poller import TelegramPoller

def main():
    """Основная функция запуска поллера"""
    token = os.getenv('TELEGRAM_TOKEN')
    if not token:
        logger.error("Не найден токен Telegram! Проверьте .env файл")
        return
    
    interval = int(os.getenv('TELEGRAM_POLL_INTERVAL', '5'))
    
    logger.info(f"Запускаем поллер Telegram с интервалом {interval} сек.")
    poller = TelegramPoller(token=token, interval=interval)
    
    if poller.start():
        logger.info("Поллер Telegram успешно запущен")
        try:
            # Бесконечный цикл для поддержания работы скрипта
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            logger.info("Получен сигнал остановки")
        finally:
            logger.info("Останавливаем поллер Telegram...")
            poller.stop()
            logger.info("Поллер Telegram остановлен")
    else:
        logger.error("Не удалось запустить поллер Telegram")

if __name__ == "__main__":
    main()