#!/usr/bin/env python3
import requests
import json

def fix_webhook():
    """Исправление URL webhook в Telegram"""
    bot_token = "7606767600:AAFGN18TMl0pUQIsQzaKiozmMKe0KBeSjyE"
    
    # 1. Сначала удалим старый webhook
    print("1. Удаляем старый webhook...")
    delete_url = f"https://api.telegram.org/bot{bot_token}/deleteWebhook"
    response = requests.get(delete_url)
    print(f"Статус удаления: {response.status_code}")
    print(f"Ответ: {response.json()}")
    print("-" * 50)
    
    # 2. Установим новый webhook с правильным URL
    print("2. Устанавливаем новый webhook...")
    webhook_url = "https://programism.ru/telegram/webhook/"
    set_url = f"https://api.telegram.org/bot{bot_token}/setWebhook?url={webhook_url}"
    response = requests.get(set_url)
    print(f"Статус установки: {response.status_code}")
    print(f"Ответ: {response.json()}")
    print("-" * 50)
    
    # 3. Проверим статус webhook
    print("3. Проверяем статус webhook...")
    info_url = f"https://api.telegram.org/bot{bot_token}/getWebhookInfo"
    response = requests.get(info_url)
    print(f"Статус проверки: {response.status_code}")
    print(f"Ответ: {json.dumps(response.json(), indent=2, ensure_ascii=False)}")
    print("-" * 50)
    
    # 4. Тестируем webhook
    print("4. Тестируем webhook...")
    test_data = {
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
        response = requests.post(webhook_url, json=test_data, headers={'Content-Type': 'application/json'})
        print(f"Статус теста: {response.status_code}")
        print(f"Ответ: {response.text}")
    except Exception as e:
        print(f"Ошибка теста: {e}")

if __name__ == "__main__":
    fix_webhook() 