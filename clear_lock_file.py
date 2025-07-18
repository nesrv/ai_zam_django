#!/usr/bin/env python
"""
Скрипт для принудительного удаления файла блокировки поллера Telegram
"""
import os
import sys
import django
import logging

# Настройка путей для Django
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.append(BASE_DIR)
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ai_zam.settings')

# Инициализация Django
django.setup()

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Импорт пути к файлу блокировки
from telegrambot.telegram_poller import LOCK_FILE

def main():
    """Удаление файла блокировки"""
    print(f"Проверка файла блокировки: {LOCK_FILE}")
    
    if os.path.exists(LOCK_FILE):
        try:
            os.remove(LOCK_FILE)
            print(f"✅ Файл блокировки успешно удален: {LOCK_FILE}")
        except Exception as e:
            print(f"❌ Ошибка при удалении файла блокировки: {e}")
            return False
    else:
        print(f"ℹ️ Файл блокировки не найден: {LOCK_FILE}")
    
    return True

if __name__ == "__main__":
    main()