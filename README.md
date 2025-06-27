# AI-ZAM Django + Telegram Bot

Django приложение с интегрированным Telegram ботом.

## 🚀 Запуск

### Основная команда
```bash
python manage.py runserver_with_bots
```

Эта команда запустит:
- Django сервер на http://127.0.0.1:8000/
- Telegram бота ne_srv_bot в фоновом режиме

### Альтернативные команды
```bash
# Только бот (без Django сервера)
python manage.py runserver_with_bots --bots-only

# Только Django сервер (без бота)
python manage.py runserver_with_bots --django-only

# Отдельный запуск бота
python manage.py run_ne_srv_bot
```

## 📋 Функции бота

- `/start` - приветствие
- `/help` - справка
- Обработка "привет" и "пока"

## 🛑 Остановка

Нажмите `Ctrl+C` для остановки сервера и бота.

---

**Готово!** 🎉 