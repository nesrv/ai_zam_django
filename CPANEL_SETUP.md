# Инструкция по настройке поллера Telegram в cPanel

## Вариант 1: Через Cron Jobs

1. Войдите в cPanel
2. Найдите раздел "Advanced" и выберите "Cron Jobs"
3. Добавьте новое задание:
   - Common Settings: выберите "Once Per Minute"
   - Command: `/usr/local/bin/python3 /home/username/public_html/cpanel_telegram_poller.py`
   
   Замените `username` на ваше имя пользователя в cPanel.

4. Нажмите "Add New Cron Job"

## Вариант 2: Через Python Selector

1. Войдите в cPanel
2. Найдите раздел "Software" и выберите "Setup Python App"
3. Нажмите "Create Application"
4. Заполните форму:
   - Python Version: выберите Python 3.9 или выше
   - Application Root: укажите путь к вашему проекту
   - Application URL: оставьте пустым
   - Application Startup File: укажите `cpanel_telegram_poller.py`
   - Application Entry Point: оставьте пустым
5. Нажмите "Create"

## Вариант 3: Через Passenger

Если ваш хостинг поддерживает Passenger, создайте файл `passenger_wsgi.py` в корне проекта:

```python
import os
import sys
import threading

# Добавляем путь к проекту
sys.path.insert(0, os.path.dirname(__file__))

# Импортируем WSGI-приложение Django
from ai_zam.wsgi import application

# Запускаем поллер в отдельном потоке
def start_telegram_poller():
    try:
        from telegrambot.telegram_poller import start_polling
        start_polling()
    except Exception as e:
        print(f"Ошибка запуска поллера: {e}")

# Запускаем поллер в отдельном потоке
poller_thread = threading.Thread(target=start_telegram_poller, daemon=True)
poller_thread.start()
```

## Проверка работы поллера

1. Проверьте логи в файле `logs/cpanel_telegram_poller.log`
2. Отправьте тестовое сообщение в Telegram-бот
3. Проверьте, что сообщение отображается на странице `/telegram/chats/`