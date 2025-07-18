#!/usr/bin/env python
"""
Скрипт для запуска поллера Telegram через cPanel
Добавьте этот скрипт в cPanel -> Cron Jobs
"""
import os
import sys
import django
import time
import logging
from dotenv import load_dotenv

# Настройка путей для Django
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(BASE_DIR)
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ai_zam.settings')

# Инициализация Django
django.setup()

# Загрузка переменных окружения
load_dotenv()

# Настройка логирования
LOG_DIR = os.path.join(BASE_DIR, 'logs')
os.makedirs(LOG_DIR, exist_ok=True)

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler(os.path.join(LOG_DIR, 'cpanel_telegram_poller.log'))
    ]
)
logger = logging.getLogger(__name__)

# Импорт поллера
from telegrambot.telegram_poller import TelegramPoller, is_another_instance_running, create_lock_file, remove_lock_file

def main():
    """Основная функция запуска поллера"""
    token = os.getenv('TELEGRAM_TOKEN')
    if not token:
        logger.error("Не найден токен Telegram! Проверьте .env файл")
        return
    
    interval = int(os.getenv('TELEGRAM_POLL_INTERVAL', '20'))
    
    # Проверяем, запущен ли уже другой экземпляр поллера
    if is_another_instance_running():
        logger.warning("Обнаружен другой запущенный экземпляр поллера, новый не будет запущен")
        return False
    
    # Создаем файл блокировки
    if not create_lock_file():
        logger.error("Не удалось создать файл блокировки, поллер не будет запущен")
        return False
    
    logger.info(f"Запускаем поллер Telegram с интервалом {interval} сек.")
    poller = TelegramPoller(token=token, interval=interval)
    
    try:
        if poller.start():
            logger.info("Поллер Telegram успешно запущен")
            # Бесконечный цикл для поддержания работы скрипта
            while True:
                time.sleep(60)  # Проверяем каждую минуту
                logger.info("Поллер работает...")
        else:
            logger.error("Не удалось запустить поллер Telegram")
            remove_lock_file()
    except KeyboardInterrupt:
        logger.info("Получен сигнал остановки")
    except Exception as e:
        logger.error(f"Ошибка в работе поллера: {e}")
    finally:
        logger.info("Останавливаем поллер Telegram...")
        poller.stop()
        remove_lock_file()
        logger.info("Поллер Telegram остановлен")

if __name__ == "__main__":
    main()