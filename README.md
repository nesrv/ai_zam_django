# AI-ZAM Django + Telegram Bot

Django приложение с интегрированным Telegram ботом.

## 🚀 Запуск

### Основная команда
```bash
python manage.py runserver
```

Эта команда запустит:
- Django сервер на http://127.0.0.1:8000/
- Интегрированный Telegram бот в фоновом режиме
- Поллер для получения сообщений из Telegram

### Альтернативные команды
```bash
# Запуск сервера без поллера Telegram
python manage.py runserver --no-poller

# Запуск с указанием интервала опроса (в секундах)
python manage.py runserver --poll-interval=10

# Только бот (без Django сервера)
python manage.py runserver_with_bots --bots-only

# Только Django сервер (без бота)
python manage.py runserver_with_bots --django-only

# Только поллер Telegram (без Django сервера)
python manage.py runserver_with_poller --poller-only

# Запуск поллера отдельным скриптом
python run_telegram_poller.py

# Статус бота и управление
http://127.0.0.1:8000/ai-agent/
```

Подробная информация о получении сообщений из Telegram находится в файле [TELEGRAM_POLLER.md](TELEGRAM_POLLER.md).

## 📋 Функции бота

- `/start` - приветствие и меню документов
- `/help` - справка по генерации документов
- Генерация строительных документов через DeepSeek AI:
  - 📄 Лимитно-заборная карта (ЛЗК)
  - 📊 Ведомость объемов работ (ВОР)
  - 📋 Техническое задание (ТЗ)
  - ❓ Опросный лист для подрядчика
  - 🔍 Акт скрытых работ
  - 📝 Пояснительная записка
- Экспорт документов в DOCX/PDF/XLS форматы
- Сохранение истории сообщений в базе данных
- Интеграция с Django моделями

## 🛑 Остановка

Нажмите `Ctrl+C` для остановки сервера и бота.

---

**Готово!** 🎉 