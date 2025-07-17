#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Скрипт для тестирования токена Telegram бота
"""
import requests
import json

# Токен из .env файла
import os
from dotenv import load_dotenv

load_dotenv()
TOKEN = os.getenv('TELEGRAM_TOKEN')

def test_bot_token(token):
    """Тестирование токена бота"""
    print(f"Тестирование токена: {token[:20]}...")
    
    try:
        # Проверяем getMe
        url = f'https://api.telegram.org/bot{token}/getMe'
        print(f"Отправляем запрос: {url}")
        
        response = requests.get(url, timeout=10)
        print(f"Статус ответа: {response.status_code}")
        print(f"Заголовки ответа: {dict(response.headers)}")
        
        if response.status_code == 200:
            result = response.json()
            print("[OK] Токен действителен!")
            print(f"Информация о боте:")
            print(f"   - ID: {result['result']['id']}")
            print(f"   - Имя: {result['result']['first_name']}")
            print(f"   - Username: @{result['result'].get('username', 'Не указан')}")
            print(f"   - Может присоединяться к группам: {result['result'].get('can_join_groups', False)}")
            print(f"   - Может читать все сообщения: {result['result'].get('can_read_all_group_messages', False)}")
            return True
        else:
            print("[ERROR] Ошибка!")
            print(f"Текст ответа: {response.text}")
            
            try:
                error_data = response.json()
                print(f"Детали ошибки: {error_data}")
            except:
                print("Не удалось разобрать JSON ошибки")
            
            return False
            
    except requests.exceptions.Timeout:
        print("[TIMEOUT] Таймаут запроса")
        return False
    except requests.exceptions.ConnectionError:
        print("[CONNECTION] Ошибка подключения к интернету")
        return False
    except Exception as e:
        print(f"[EXCEPTION] Неожиданная ошибка: {e}")
        return False

def test_webhook_info(token):
    """Проверка информации о webhook"""
    print(f"\nПроверяем webhook...")
    
    try:
        url = f'https://api.telegram.org/bot{token}/getWebhookInfo'
        response = requests.get(url, timeout=10)
        
        if response.status_code == 200:
            result = response.json()
            webhook_info = result['result']
            print(f"Webhook URL: {webhook_info.get('url', 'Не установлен')}")
            print(f"Pending updates: {webhook_info.get('pending_update_count', 0)}")
            if webhook_info.get('last_error_message'):
                print(f"[ERROR] Последняя ошибка: {webhook_info['last_error_message']}")
        else:
            print(f"[ERROR] Ошибка получения webhook info: {response.status_code}")
            
    except Exception as e:
        print(f"[EXCEPTION] Ошибка webhook info: {e}")

def test_updates(token):
    """Проверка получения обновлений"""
    print(f"\nПроверяем получение обновлений...")
    
    try:
        url = f'https://api.telegram.org/bot{token}/getUpdates'
        response = requests.get(url, timeout=10)
        
        if response.status_code == 200:
            result = response.json()
            updates = result['result']
            print(f"Количество обновлений: {len(updates)}")
            
            if updates:
                latest = updates[-1]
                print(f"Последнее обновление ID: {latest.get('update_id')}")
                if 'message' in latest:
                    msg = latest['message']
                    print(f"Последнее сообщение от: {msg.get('from', {}).get('first_name', 'Неизвестно')}")
                    print(f"Текст: {msg.get('text', 'Нет текста')[:50]}...")
        else:
            print(f"[ERROR] Ошибка получения обновлений: {response.status_code}")
            print(f"Ответ: {response.text}")
            
    except Exception as e:
        print(f"[EXCEPTION] Ошибка получения обновлений: {e}")

if __name__ == "__main__":
    print("Запуск тестирования Telegram бота")
    print("=" * 50)
    
    # Основной тест токена
    if test_bot_token(TOKEN):
        # Дополнительные тесты
        test_webhook_info(TOKEN)
        test_updates(TOKEN)
    else:
        print("\nВозможные причины ошибки 401:")
        print("1. Токен недействителен или устарел")
        print("2. Бот был удален или заблокирован")
        print("3. Токен содержит лишние символы")
        print("4. Проблемы с сетевым подключением")
        print("\nРекомендации:")
        print("1. Создайте нового бота через @BotFather")
        print("2. Получите новый токен")
        print("3. Обновите .env файл")
    
    print("\n" + "=" * 50)
    print("Тестирование завершено")