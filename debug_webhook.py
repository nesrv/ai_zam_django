#!/usr/bin/env python3
import requests
import json

def debug_webhook():
    """Детальная диагностика webhook"""
    webhook_url = "https://programism.ru/telegram/webhook/"
    
    # Тест 1: Простое сообщение /start
    print("Тест 1: Команда /start")
    test_data_1 = {
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
        response = requests.post(webhook_url, json=test_data_1, headers={'Content-Type': 'application/json'})
        print(f"Статус: {response.status_code}")
        print(f"Заголовки: {dict(response.headers)}")
        print(f"Ответ: {response.text}")
        print("-" * 50)
    except Exception as e:
        print(f"Ошибка: {e}")
        print("-" * 50)
    
    # Тест 2: Пустое сообщение
    print("Тест 2: Пустое сообщение")
    test_data_2 = {
        "update_id": 123456790,
        "message": {
            "message_id": 2,
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
            "text": ""
        }
    }
    
    try:
        response = requests.post(webhook_url, json=test_data_2, headers={'Content-Type': 'application/json'})
        print(f"Статус: {response.status_code}")
        print(f"Ответ: {response.text}")
        print("-" * 50)
    except Exception as e:
        print(f"Ошибка: {e}")
        print("-" * 50)
    
    # Тест 3: Сообщение без text
    print("Тест 3: Сообщение без text")
    test_data_3 = {
        "update_id": 123456791,
        "message": {
            "message_id": 3,
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
            "date": 1234567890
        }
    }
    
    try:
        response = requests.post(webhook_url, json=test_data_3, headers={'Content-Type': 'application/json'})
        print(f"Статус: {response.status_code}")
        print(f"Ответ: {response.text}")
        print("-" * 50)
    except Exception as e:
        print(f"Ошибка: {e}")
        print("-" * 50)
    
    # Тест 4: Проверка статуса webhook
    print("Тест 4: Проверка статуса webhook")
    try:
        response = requests.get(webhook_url + "status/")
        print(f"Статус: {response.status_code}")
        print(f"Ответ: {response.text}")
        print("-" * 50)
    except Exception as e:
        print(f"Ошибка: {e}")
        print("-" * 50)

if __name__ == "__main__":
    debug_webhook() 