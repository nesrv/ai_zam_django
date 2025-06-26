#!/usr/bin/env python3
import requests
import json

def check_webhook_status():
    """Проверка статуса webhook"""
    bot_token = "7606767600:AAFGN18TMl0pUQIsQzaKiozmMKe0KBeSjyE"
    url = f"https://api.telegram.org/bot{bot_token}/getWebhookInfo"
    
    try:
        response = requests.get(url)
        data = response.json()
        
        print("=== СТАТУС WEBHOOK ===")
        print(f"Статус запроса: {response.status_code}")
        print(f"Webhook установлен: {data.get('ok')}")
        
        if data.get('ok') and data.get('result'):
            result = data['result']
            print(f"URL: {result.get('url')}")
            print(f"Накопившиеся сообщения: {result.get('pending_update_count')}")
            print(f"Последняя ошибка: {result.get('last_error_message')}")
            print(f"Дата последней ошибки: {result.get('last_error_date')}")
            print(f"IP адрес: {result.get('ip_address')}")
            
            if result.get('pending_update_count', 0) > 0:
                print("\n⚠️  Есть накопившиеся сообщения!")
                print("Это означает, что Telegram пытается доставить сообщения.")
                print("Попробуйте отправить сообщение боту в Telegram.")
            else:
                print("\n✅ Нет накопившихся сообщений!")
                print("Webhook работает корректно.")
        
        return data
        
    except Exception as e:
        print(f"Ошибка: {e}")
        return None

if __name__ == "__main__":
    check_webhook_status() 