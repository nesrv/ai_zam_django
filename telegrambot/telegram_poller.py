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
    
    def __init__(self, token=None, interval=20):
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
            try:
                # Отправляем запрос на сброс вебхука, чтобы освободить сессию getUpdates
                url = f"https://api.telegram.org/bot{self.token}/deleteWebhook?drop_pending_updates=true"
                requests.get(url, timeout=5)
                logger.info("Вебхук сброшен для освобождения сессии getUpdates")
            except Exception as e:
                logger.error(f"Ошибка при сбросе вебхука: {e}")
            
            # Ожидаем завершения потока
            self.thread.join(timeout=5)
        logger.info("Поллер Telegram остановлен")
    
    def _cleanup_processed_updates(self):
        """Очистка старых записей из таблицы ProcessedUpdate"""
        try:
            from .models import ProcessedUpdate
            from django.utils import timezone
            import datetime
            
            # Удаляем записи старше 1 дня
            one_day_ago = timezone.now() - datetime.timedelta(days=1)
            deleted_count = ProcessedUpdate.objects.filter(processed_at__lt=one_day_ago).delete()[0]
            
            if deleted_count > 0:
                logger.info(f"Удалено {deleted_count} старых записей из таблицы ProcessedUpdate")
        except Exception as e:
            logger.error(f"Ошибка при очистке таблицы ProcessedUpdate: {e}")
    
    def _polling_loop(self):
        """Основной цикл опроса API Telegram"""
        cleanup_counter = 0
        while self.is_running:
            try:
                self._get_updates()
                
                # Очищаем старые записи каждые 100 циклов
                cleanup_counter += 1
                if cleanup_counter >= 100:
                    self._cleanup_processed_updates()
                    cleanup_counter = 0
                
                time.sleep(self.interval)
            except Exception as e:
                logger.error(f"Ошибка в цикле опроса: {e}")
                time.sleep(self.interval * 2)  # Увеличиваем интервал при ошибке
    
    def _get_updates(self):
        """Получение обновлений от API Telegram"""
        try:
            # Проверяем, что мы единственный экземпляр поллера
            if is_another_instance_running():
                logger.warning("Обнаружен другой экземпляр поллера, пропускаем получение обновлений")
                return
            
            # Сначала пробуем сбросить вебхук, чтобы избежать конфликтов
            try:
                reset_url = f"https://api.telegram.org/bot{self.token}/deleteWebhook?drop_pending_updates=false"
                reset_response = requests.get(reset_url, timeout=5)
                if reset_response.status_code == 200:
                    logger.info("Вебхук успешно сброшен перед получением обновлений")
            except Exception as e:
                logger.warning(f"Ошибка при сбросе вебхука: {e}")
            
            # Добавляем небольшую задержку после сброса вебхука
            time.sleep(1)
            
            url = f"https://api.telegram.org/bot{self.token}/getUpdates"
            params = {
                'offset': self.last_update_id + 1,
                'timeout': 10,  # Уменьшаем таймаут для более частых проверок
                'allowed_updates': json.dumps(['message', 'edited_message', 'channel_post'])
            }
            
            # Используем новую сессию для каждого запроса
            with requests.Session() as session:
                response = session.get(url, params=params, timeout=15)
                
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
                    # Проверяем, не обрабатывали ли мы уже это обновление
                    from .models import ProcessedUpdate
                    update_id = str(update.get('update_id'))
                    if ProcessedUpdate.objects.filter(update_id=update_id).exists():
                        logger.info(f"Обновление {update_id} уже было обработано ранее, пропускаем")
                        continue
                    
                    # Сохраняем информацию об обработанном обновлении
                    ProcessedUpdate.objects.create(update_id=update_id)
                    
                    # Обрабатываем обновление
                    self._process_update(update)
                    
                    # Обновляем last_update_id
                    if int(update_id) > self.last_update_id:
                        self.last_update_id = int(update_id)
                
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

# Файл блокировки для предотвращения конфликтов
import tempfile
import socket

# Используем абсолютный путь для файла блокировки
LOCK_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'telegram_poller.lock')

# Добавляем сокет для блокировки процесса
LOCK_SOCKET = None
LOCK_SOCKET_PORT = 12345  # Уникальный порт для блокировки

def is_another_instance_running():
    """Проверка, запущен ли уже другой экземпляр поллера"""
    global LOCK_SOCKET
    try:
        # Пытаемся создать сокет на указанном порту
        LOCK_SOCKET = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        LOCK_SOCKET.bind(('localhost', LOCK_SOCKET_PORT))
        LOCK_SOCKET.setblocking(False)
        logger.info(f"Успешно получена блокировка на порту {LOCK_SOCKET_PORT}")
        return False
    except socket.error:
        logger.warning(f"Порт {LOCK_SOCKET_PORT} уже занят, другой экземпляр поллера уже запущен")
        return True
    except Exception as e:
        logger.error(f"Ошибка при проверке блокировки сокета: {e}")
        # При ошибке проверяем файл блокировки как запасной вариант
        if os.path.exists(LOCK_FILE):
            try:
                file_time = os.path.getmtime(LOCK_FILE)
                current_time = time.time()
                # Если файл старше 5 минут, считаем его устаревшим
                if current_time - file_time > 300:  # 5 минут = 300 секунд
                    logger.warning("Найден устаревший файл блокировки, удаляем")
                    try:
                        os.remove(LOCK_FILE)
                        return False
                    except Exception as e:
                        logger.error(f"Не удалось удалить устаревший файл блокировки: {e}")
                        return False
                return True
            except Exception as e:
                logger.error(f"Ошибка при проверке времени файла блокировки: {e}")
                return False
        return False

def create_lock_file():
    """Создание файла блокировки"""
    try:
        # Создаем файл блокировки
        with open(LOCK_FILE, 'w') as f:
            f.write(str(datetime.now()))
        logger.info(f"Файл блокировки создан: {LOCK_FILE}")
        return True
    except Exception as e:
        logger.error(f"Не удалось создать файл блокировки: {e}")
        return False

def remove_lock_file():
    """Удаление файла блокировки и освобождение сокета"""
    global LOCK_SOCKET
    try:
        # Закрываем сокет, если он был создан
        if LOCK_SOCKET:
            try:
                LOCK_SOCKET.close()
                LOCK_SOCKET = None
                logger.info(f"Сокет на порту {LOCK_SOCKET_PORT} освобожден")
            except Exception as e:
                logger.error(f"Ошибка при закрытии сокета: {e}")
        
        # Удаляем файл блокировки
        if os.path.exists(LOCK_FILE):
            os.remove(LOCK_FILE)
            logger.info(f"Файл блокировки удален: {LOCK_FILE}")
        
        return True
    except Exception as e:
        logger.error(f"Не удалось удалить файл блокировки: {e}")
        return False

def start_polling():
    """Запуск поллера с настройками по умолчанию"""
    global poller
    
    try:
        # Проверяем, запущен ли уже другой экземпляр поллера
        if is_another_instance_running():
            logger.warning("Обнаружен другой запущенный экземпляр поллера. Новый экземпляр не будет запущен.")
            return False
        
        # Создаем файл блокировки
        create_lock_file()
        
        # Создаем и запускаем поллер
        if poller is None:
            poller = TelegramPoller()
        
        success = poller.start()
        
        # Если не удалось запустить поллер, удаляем файл блокировки
        if not success:
            remove_lock_file()
            
        return success
    except Exception as e:
        logger.error(f"Ошибка при запуске поллера: {e}")
        
        # Удаляем файл блокировки при ошибке
        remove_lock_file()
        return False

def stop_polling():
    """Остановка поллера"""
    global poller
    if poller:
        poller.stop()
        poller = None
    
    # Удаляем файл блокировки
    remove_lock_file()