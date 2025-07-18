#!/usr/bin/env python
"""
Скрипт для проверки токена Telegram бота
"""
import os
import sys
import requests
import json
from dotenv import load_dotenv
import pathlib

# Получаем путь к корневой папке проекта
BASE_DIR = pathlib.Path(__file__).resolve().parent
ENV_FILE = BASE_DIR / '.env'

# Загружаем переменные окружения
load_dotenv(ENV_FILE)

# Получаем токен бота
token = os.getenv('TELEGRAM_TOKEN')

if not token:
    print("ОШИБКА: Токен Telegram бота не найден в переменных окружения!")
    print(f"Проверьте файл .env в директории: {ENV_FILE}")
    sys.exit(1)

# Проверяем токен
url = f'https://api.telegram.org/bot{token}/getMe'
try:
    response = requests.get(url)
    response.raise_for_status()
    
    result = response.json()
    if result.get('ok'):
        bot_info = result.get('result', {})
        print(f"✅ Токен действителен!")
        print(f"Имя бота: {bot_info.get('first_name')}")
        print(f"Имя пользователя: @{bot_info.get('username')}")
        print(f"ID бота: {bot_info.get('id')}")
    else:
        print(f"❌ Ошибка проверки токена: {result}")
except Exception as e:
    print(f"❌ Ошибка при проверке токена: {e}")
    sys.exit(1)