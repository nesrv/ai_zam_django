#!/usr/bin/env python3
import os
import requests
from dotenv import load_dotenv

def test_telegram_token():
    """Проверка TELEGRAM_TOKEN"""
    # Загружаем переменные окружения
    load_dotenv()
    
    # Получаем токен
    token = os.getenv('TELEGRAM_TOKEN')
    
    print("=== ПРОВЕРКА TELEGRAM_TOKEN ===")
    print(f"Токен найден: {'Да' if token else 'Нет'}")
    
    if token:
        print(f"Токен: {token[:10]}...{token[-10:]}")
        
        # Проверяем валидность токена
        url = f"https://api.telegram.org/bot{token}/getMe"
        
        try:
            response = requests.get(url)
            data = response.json()
            
            if data.get('ok'):
                bot_info = data['result']
                print(f"✅ Токен валидный!")
                print(f"Имя бота: {bot_info.get('first_name')}")
                print(f"Username: @{bot_info.get('username')}")
                print(f"ID бота: {bot_info.get('id')}")
            else:
                print(f"❌ Токен невалидный: {data.get('description')}")
                
        except Exception as e:
            print(f"❌ Ошибка проверки токена: {e}")
    else:
        print("❌ TELEGRAM_TOKEN не найден в .env файле!")
        print("Добавьте в .env файл строку:")
        print("TELEGRAM_TOKEN=7606767600:AAFGN18TMl0pUQIsQzaKiozmMKe0KBeSjyE")

if __name__ == "__main__":
    test_telegram_token() 