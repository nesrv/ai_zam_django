#!/usr/bin/env python3
import requests
import json

def test_webhook():
    """Тестирование Telegram webhook"""
    url = 'https://programism.ru/telegram/webhook/'
    
    # Тест 1: Пустой JSON
    print("Тест 1: Пустой JSON")
    try:
        response = requests.post(url, json={}, headers={'Content-Type': 'application/json'})
        print(f"Статус: {response.status_code}")
        print(f"Ответ: {response.text}")
        print("-" * 50)
    except Exception as e:
        print(f"Ошибка: {e}")
        print("-" * 50)
    
    # Тест 2: Валидное сообщение Telegram
    print("Тест 2: Валидное сообщение Telegram")
    telegram_message = {
        "update_id": 123456789,
        "message": {
            "message_id": 1,
            "from": {
                "id": 123456789,
                "is_bot": False,
                "first_name": "Test",
                "username": "testuser"
            },
            "chat": {
                "id": 123456789,
                "first_name": "Test",
                "username": "testuser",
                "type": "private"
            },
            "date": 1234567890,
            "text": "/start"
        }
    }
    
    try:
        response = requests.post(url, json=telegram_message, headers={'Content-Type': 'application/json'})
        print(f"Статус: {response.status_code}")
        print(f"Ответ: {response.text}")
        print("-" * 50)
    except Exception as e:
        print(f"Ошибка: {e}")
        print("-" * 50)
    
    # Тест 3: Проверка статуса webhook
    print("Тест 3: Проверка статуса webhook")
    try:
        response = requests.get('https://programism.ru/telegram/webhook/status/')
        print(f"Статус: {response.status_code}")
        print(f"Ответ: {response.text}")
        print("-" * 50)
    except Exception as e:
        print(f"Ошибка: {e}")
        print("-" * 50)

if __name__ == "__main__":
    test_webhook() 