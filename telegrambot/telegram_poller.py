import os
import logging
import threading
import time
import requests
import json
from django.utils import timezone
from datetime import datetime

# Настройка логирования
logger = logging.getLogger(__name__)

class TelegramPoller:
    """Класс для периодического опроса API Telegram"""
    
    def __init__(self, token=None, interval=5):
        """
        Инициализация поллера
        :param token: Токен Telegram бота
        :param interval: Интервал опроса в секундах
        """
        self.token = token or os.getenv('TELEGRAM_TOKEN')
        self.interval = interval
        self.last_update_id = 0
        self.is_running = False
        self.thread = None
        
        if not self.token:
            logger.error("Не указан токен Telegram бота")
    
    def start(self):
        """Запуск поллера в отдельном потоке"""
        if self.is_running:
            logger.warning("Поллер уже запущен")
            return False
        
        if not self.token:
            logger.error("Невозможно запустить поллер без токена")
            return False
        
        self.is_running = True
        self.thread = threading.Thread(target=self._polling_loop, daemon=True)
        self.thread.start()
        logger.info(f"Поллер Telegram запущен с интервалом {self.interval} сек.")
        return True
    
    def stop(self):
        """Остановка поллера"""
        self.is_running = False
        if self.thread and self.thread.is_alive():
            self.thread.join(timeout=5)
        logger.info("Поллер Telegram остановлен")
    
    def _polling_loop(self):
        """Основной цикл опроса API Telegram"""
        while self.is_running:
            try:
                self._get_updates()
                time.sleep(self.interval)
            except Exception as e:
                logger.error(f"Ошибка в цикле опроса: {e}")
                time.sleep(self.interval * 2)  # Увеличиваем интервал при ошибке
    
    def _get_updates(self):
        """Получение обновлений от API Telegram"""
        try:
            url = f"https://api.telegram.org/bot{self.token}/getUpdates"
            params = {
                'offset': self.last_update_id + 1,
                'timeout': 30,
                'allowed_updates': json.dumps(['message', 'edited_message', 'channel_post'])
            }
            
            response = requests.get(url, params=params, timeout=35)
            
            if response.status_code != 200:
                logger.error(f"Ошибка API Telegram: {response.status_code} - {response.text}")
                return
            
            data = response.json()
            
            if not data.get('ok'):
                logger.error(f"API вернул ошибку: {data}")
                return
            
            updates = data.get('result', [])
            
            if not updates:
                return
            
            # Обрабатываем каждое обновление
            for update in updates:
                self._process_update(update)
                
                # Обновляем last_update_id
                if update['update_id'] > self.last_update_id:
                    self.last_update_id = update['update_id']
            
            logger.info(f"Получено {len(updates)} обновлений, последний ID: {self.last_update_id}")
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Ошибка запроса к API Telegram: {e}")
        except json.JSONDecodeError as e:
            logger.error(f"Ошибка декодирования JSON: {e}")
        except Exception as e:
            logger.error(f"Неожиданная ошибка при получении обновлений: {e}")
    
    def _process_update(self, update):
        """Обработка одного обновления"""
        try:
            # Импортируем здесь, чтобы избежать циклических импортов
            from .services import process_telegram_message
            
            # Обрабатываем сообщение
            if 'message' in update:
                logger.info(f"Получено новое сообщение: {update['message'].get('text', '')[:50]}...")
                process_telegram_message(update['message'])
            elif 'edited_message' in update:
                logger.info(f"Получено отредактированное сообщение: {update['edited_message'].get('text', '')[:50]}...")
                process_telegram_message(update['edited_message'])
            elif 'channel_post' in update:
                logger.info(f"Получено сообщение из канала: {update['channel_post'].get('text', '')[:50]}...")
                process_telegram_message(update['channel_post'])
            else:
                logger.info(f"Получено обновление неизвестного типа: {update}")
            
        except Exception as e:
            logger.error(f"Ошибка обработки обновления {update.get('update_id')}: {e}")


# Глобальный экземпляр поллера
poller = None

def start_polling():
    """Запуск поллера с настройками по умолчанию"""
    global poller
    if poller is None:
        poller = TelegramPoller()
    
    return poller.start()

def stop_polling():
    """Остановка поллера"""
    global poller
    if poller:
        poller.stop()
        poller = None