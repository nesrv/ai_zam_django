#!/usr/bin/env python
"""
Скрипт для очистки всех файлов блокировки и сброса состояния поллера Telegram
"""
import os
import sys
import django
import socket
import logging
import requests
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
        logging.FileHandler('telegram_poller_reset.log')
    ]
)
logger = logging.getLogger(__name__)

def clear_lock_files():
    """Очистка всех файлов блокировки"""
    try:
        # Удаляем файл блокировки в текущей директории
        lock_file = 'telegram_poller.lock'
        if os.path.exists(lock_file):
            os.remove(lock_file)
            logger.info(f"Файл блокировки удален: {lock_file}")
        
        # Удаляем файл блокировки в директории модуля
        module_lock_file = os.path.join('telegrambot', 'telegram_poller.lock')
        if os.path.exists(module_lock_file):
            os.remove(module_lock_file)
            logger.info(f"Файл блокировки удален из директории модуля: {module_lock_file}")
        
        # Освобождаем порт блокировки
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            sock.bind(('localhost', 12345))
            logger.info("Порт 12345 успешно освобожден")
            sock.close()
        except socket.error:
            logger.warning("Не удалось освободить порт 12345, возможно он не занят")
        
        return True
    except Exception as e:
        logger.error(f"Ошибка при очистке файлов блокировки: {e}")
        return False

def clear_processed_updates():
    """Очистка таблицы обработанных обновлений"""
    try:
        from telegrambot.models import ProcessedUpdate
        count = ProcessedUpdate.objects.all().count()
        ProcessedUpdate.objects.all().delete()
        logger.info(f"Удалено {count} записей из таблицы обработанных обновлений")
        return True
    except Exception as e:
        logger.error(f"Ошибка при очистке таблицы обработанных обновлений: {e}")
        return False

def reset_telegram_webhook():
    """Сброс вебхука Telegram"""
    try:
        token = os.getenv('TELEGRAM_TOKEN')
        if not token:
            logger.error("Не найден токен Telegram! Проверьте .env файл")
            return False
        
        url = f"https://api.telegram.org/bot{token}/deleteWebhook?drop_pending_updates=true"
        response = requests.get(url, timeout=5)
        
        if response.status_code == 200:
            logger.info("Вебхук Telegram успешно сброшен")
            return True
        else:
            logger.error(f"Ошибка сброса вебхука: {response.status_code} - {response.text}")
            return False
    except Exception as e:
        logger.error(f"Ошибка при сбросе вебхука: {e}")
        return False

def main():
    """Основная функция скрипта"""
    logger.info("Начинаем сброс состояния поллера Telegram...")
    
    # Очищаем файлы блокировки
    clear_lock_files()
    
    # Очищаем таблицу обработанных обновлений
    clear_processed_updates()
    
    # Сбрасываем вебхук Telegram
    reset_telegram_webhook()
    
    logger.info("Сброс состояния поллера Telegram завершен")

if __name__ == "__main__":
    main()