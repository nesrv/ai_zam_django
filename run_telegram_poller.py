#!/usr/bin/env python
"""
Скрипт для запуска поллера Telegram отдельно от Django
"""
import logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('/path/to/logs/telegram_poller.log')
    ]
)


import os
import sys
import django
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
        logging.FileHandler('telegram_poller.log')
    ]
)
logger = logging.getLogger(__name__)

# Импорт поллера
from telegrambot.telegram_poller import TelegramPoller

def setup_webhook():
    """Настройка вебхука для получения обновлений"""
    token = os.getenv('TELEGRAM_TOKEN')
    if not token:
        logger.error("Не найден токен Telegram! Проверьте .env файл")
        return False
    
    # Сначала удаляем существующий вебхук
    try:
        import requests
        delete_url = f"https://api.telegram.org/bot{token}/deleteWebhook?drop_pending_updates=true"
        response = requests.get(delete_url, timeout=5)
        if response.status_code == 200:
            logger.info("Существующий вебхук успешно удален")
        else:
            logger.error(f"Ошибка при удалении вебхука: {response.status_code} - {response.text}")
            return False
    except Exception as e:
        logger.error(f"Ошибка при удалении вебхука: {e}")
        return False
    
    # Теперь запускаем поллер в режиме длинного поллинга
    interval = int(os.getenv('TELEGRAM_POLL_INTERVAL', '30'))
    logger.info(f"Запускаем поллер Telegram в режиме длинного поллинга с интервалом {interval} сек.")
    
    # Удаляем файлы блокировки
    from telegrambot.telegram_poller import remove_lock_file
    remove_lock_file()
    
    return True

def main():
    """Основная функция запуска поллера"""
    # Настраиваем вебхук
    if not setup_webhook():
        logger.error("Не удалось настроить вебхук")
        return
    
    token = os.getenv('TELEGRAM_TOKEN')
    interval = int(os.getenv('TELEGRAM_POLL_INTERVAL', '30'))
    
    # Используем длинный поллинг вместо обычного поллера
    try:
        import requests
        logger.info("Запуск длинного поллинга Telegram...")
        
        # Очищаем таблицу обработанных обновлений
        from telegrambot.models import ProcessedUpdate
        ProcessedUpdate.objects.all().delete()
        logger.info("Таблица обработанных обновлений очищена")
        
        # Используем длинный поллинг с большим таймаутом
        last_update_id = 0
        while True:
            try:
                url = f"https://api.telegram.org/bot{token}/getUpdates"
                params = {
                    'offset': last_update_id + 1,
                    'timeout': 60,  # Длинный поллинг с таймаутом 60 секунд
                    'allowed_updates': json.dumps(['message', 'edited_message', 'channel_post'])
                }
                
                # Используем новую сессию для каждого запроса
                with requests.Session() as session:
                    response = session.get(url, params=params, timeout=70)  # Таймаут запроса больше таймаута поллинга
                    
                    if response.status_code != 200:
                        logger.error(f"Ошибка API Telegram: {response.status_code} - {response.text}")
                        time.sleep(interval)  # Пауза перед следующей попыткой
                        continue
                    
                    data = response.json()
                    
                    if not data.get('ok'):
                        logger.error(f"API вернул ошибку: {data}")
                        time.sleep(interval)
                        continue
                    
                    updates = data.get('result', [])
                    
                    if not updates:
                        continue  # Нет новых обновлений, продолжаем поллинг
                    
                    # Обрабатываем каждое обновление
                    for update in updates:
                        # Проверяем, не обрабатывали ли мы уже это обновление
                        update_id = update.get('update_id')
                        if ProcessedUpdate.objects.filter(update_id=str(update_id)).exists():
                            logger.info(f"Обновление {update_id} уже было обработано ранее, пропускаем")
                            continue
                        
                        # Сохраняем информацию об обработанном обновлении
                        ProcessedUpdate.objects.create(update_id=str(update_id))
                        
                        # Обрабатываем сообщение
                        from telegrambot.services import process_telegram_message
                        
                        if 'message' in update:
                            logger.info(f"Получено новое сообщение: {update['message'].get('text', '')[:50]}...")
                            process_telegram_message(update['message'])
                        elif 'edited_message' in update:
                            logger.info(f"Получено отредактированное сообщение: {update['edited_message'].get('text', '')[:50]}...")
                            process_telegram_message(update['edited_message'])
                        elif 'channel_post' in update:
                            logger.info(f"Получено сообщение из канала: {update['channel_post'].get('text', '')[:50]}...")
                            process_telegram_message(update['channel_post'])
                        
                        # Обновляем last_update_id
                        if update_id > last_update_id:
                            last_update_id = update_id
                    
                    logger.info(f"Получено {len(updates)} обновлений, последний ID: {last_update_id}")
                    
                    # Очищаем старые записи каждые 100 циклов
                    if last_update_id % 100 == 0:
                        from django.utils import timezone
                        import datetime
                        one_day_ago = timezone.now() - datetime.timedelta(days=1)
                        ProcessedUpdate.objects.filter(processed_at__lt=one_day_ago).delete()
                        logger.info("Старые записи обработанных обновлений удалены")
            
            except KeyboardInterrupt:
                logger.info("Получен сигнал остановки")
                break
            except Exception as e:
                logger.error(f"Ошибка в цикле поллинга: {e}")
                time.sleep(interval)  # Пауза перед следующей попыткой
    
    except Exception as e:
        logger.error(f"Критическая ошибка при запуске длинного поллинга: {e}")
    finally:
        logger.info("Длинный поллинг Telegram остановлен")

if __name__ == "__main__":
    main()