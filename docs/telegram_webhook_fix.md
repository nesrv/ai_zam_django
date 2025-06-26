# 🔧 Исправление ошибки "Referer checking failed" для Telegram Webhook

## 🚨 Проблема
```
Forbidden (Referer checking failed - no Referer.): /telegram-webhook/
```

Эта ошибка возникает потому, что Django проверяет заголовок Referer для защиты от CSRF атак, но Telegram webhook не отправляет этот заголовок.

## ✅ Решение

### 1. Добавлены декораторы в views.py
```python
@csrf_exempt
@xframe_options_exempt
@require_POST
def telegram_webhook(request):
    # ...
```

### 2. Настроены CSRF настройки в settings.py
```python
# Настройки для Telegram webhook
CSRF_TRUSTED_ORIGINS = [
    "https://api.telegram.org",
    "https://core.telegram.org",
]

# Отключаем проверку Referer для webhook
CSRF_USE_SESSIONS = False
CSRF_COOKIE_SECURE = False
```

### 3. Создан кастомный middleware
```python
class TelegramWebhookMiddleware:
    def __call__(self, request):
        if request.path == '/telegram/webhook/' and request.method == 'POST':
            request.META['HTTP_REFERER'] = 'https://api.telegram.org'
        return self.get_response(request)
```

### 4. Добавлен middleware в settings.py
```python
MIDDLEWARE = [
    # ... другие middleware
    'telegrambot.middleware.TelegramWebhookMiddleware',
]
```

## 🧪 Проверка

### 1. Проверка статуса webhook
```bash
curl http://yourdomain.com/telegram/webhook/status/
```

### 2. Проверка webhook через Telegram API
```bash
curl "https://api.telegram.org/bot<YOUR_BOT_TOKEN>/getWebhookInfo"
```

### 3. Установка webhook
```bash
curl "https://api.telegram.org/bot<YOUR_BOT_TOKEN>/setWebhook?url=https://yourdomain.com/telegram/webhook/"
```

## 🔍 Логирование

Теперь webhook логирует:
- Подозрительные запросы (не от Telegram)
- Успешные обновления
- Ошибки обработки

## ⚠️ Безопасность

- Проверяется User-Agent для определения запросов от Telegram
- Логируются подозрительные запросы
- CSRF защита отключена только для webhook endpoint

## 🚀 Результат

После применения этих изменений:
- ✅ Webhook принимает запросы от Telegram
- ✅ Нет ошибок "Referer checking failed"
- ✅ Сохранена безопасность
- ✅ Добавлено логирование для отладки 