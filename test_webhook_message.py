#!/usr/bin/env python
import requests
import json

def test_webhook_message():
    """Тестирует webhook с отправкой тестового сообщения"""
    
    # URL webhook
    webhook_url = "http://127.0.0.1:8000/telegram/webhook/"
    
    # Тестовые данные от Telegram
    test_update = {
        "update_id": 999999999,
        "message": {
            "message_id": 100,
            "from": {
                "id": 123456789,
                "is_bot": False,
                "first_name": "Test",
                "username": "testuser",
                "language_code": "ru"
            },
            "chat": {
                "id": 123456789,
                "first_name": "Test",
                "username": "testuser",
                "type": "private"
            },
            "date": 1640995200,
            "text": "Тестовое сообщение для проверки записи в БД"
        }
    }
    
    print(f"Отправляю тестовое сообщение на {webhook_url}")
    print(f"Данные: {json.dumps(test_update, indent=2, ensure_ascii=False)}")
    
    try:
        response = requests.post(
            webhook_url,
            json=test_update,
            headers={'Content-Type': 'application/json'},
            timeout=10
        )
        
        print(f"\nСтатус ответа: {response.status_code}")
        print(f"Содержимое ответа: {response.text}")
        
        if response.status_code == 200:
            print("✅ Webhook успешно обработал сообщение")
        else:
            print("❌ Webhook вернул ошибку")
            
    except Exception as e:
        print(f"❌ Ошибка при отправке: {e}")

if __name__ == "__main__":
    test_webhook_message() 