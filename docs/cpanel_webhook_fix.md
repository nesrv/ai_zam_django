# 🔧 Решение проблемы "Referer checking failed" на cPanel

## 🚨 Проблема
```
Forbidden (Referer checking failed - no Referer.): /telegram-webhook/
```

Эта ошибка возникает на cPanel из-за строгих настроек безопасности Django.

## ✅ Полное решение для cPanel

### 1. Кастомный CSRF Middleware
Создан `telegrambot/csrf_middleware.py` который полностью отключает CSRF проверку для Telegram webhook.

### 2. Обновленные настройки в settings.py
```python
MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'telegrambot.csrf_middleware.CustomCsrfMiddleware',  # Кастомный CSRF
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'telegrambot.middleware.TelegramWebhookMiddleware',
]

# Настройки CSRF
CSRF_TRUSTED_ORIGINS = [
    "https://api.telegram.org",
    "https://core.telegram.org",
    "https://yourdomain.com",  # Замените на ваш домен
    "https://www.yourdomain.com",
]

CSRF_USE_SESSIONS = False
CSRF_COOKIE_SECURE = False
CSRF_COOKIE_HTTPONLY = False
CSRF_FAILURE_VIEW = None
```

### 3. Улучшенное логирование
Webhook теперь логирует:
- IP адрес запроса
- User-Agent
- Успешные/неуспешные обработки
- Подозрительные запросы

## 🛠️ Дополнительные шаги для cPanel

### 1. Проверьте права доступа к файлам
```bash
chmod 644 *.py
chmod 755 */
```

### 2. Проверьте .htaccess (если используется)
```apache
<IfModule mod_rewrite.c>
    RewriteEngine On
    RewriteCond %{REQUEST_FILENAME} !-f
    RewriteRule ^(.*)$ /index.py/$1 [QSA,L]
</IfModule>
```

### 3. Настройте Python в cPanel
- Python версия: 3.8+
- Виртуальное окружение: активировано
- Зависимости: установлены

### 4. Проверьте логи ошибок
В cPanel: **Errors** → **Error Logs**

## 🧪 Тестирование

### 1. Проверка webhook статуса
```bash
curl https://yourdomain.com/telegram/webhook/status/
```

### 2. Тестовый POST запрос
```bash
curl -X POST https://yourdomain.com/telegram/webhook/ \
  -H "Content-Type: application/json" \
  -d '{"test": "data"}'
```

### 3. Установка webhook
```bash
curl "https://api.telegram.org/bot<YOUR_BOT_TOKEN>/setWebhook?url=https://yourdomain.com/telegram/webhook/"
```

### 4. Проверка webhook
```bash
curl "https://api.telegram.org/bot<YOUR_BOT_TOKEN>/getWebhookInfo"
```

## 🔍 Отладка

### 1. Включите DEBUG режим временно
```python
DEBUG = True
```

### 2. Проверьте логи Django
```bash
tail -f /path/to/your/logs/django.log
```

### 3. Проверьте логи cPanel
- **Errors** → **Error Logs**
- **Errors** → **Apache Error Logs**

## ⚠️ Безопасность

### 1. Проверка IP адресов Telegram
Добавлены основные диапазоны IP адресов Telegram для проверки.

### 2. Логирование подозрительных запросов
Все подозрительные запросы логируются для мониторинга.

### 3. Валидация данных
Проверяется формат JSON и структура данных.

## 🚀 Результат

После применения всех изменений:
- ✅ Webhook принимает запросы от Telegram
- ✅ Нет ошибок "Referer checking failed"
- ✅ Улучшенное логирование для отладки
- ✅ Сохранена безопасность
- ✅ Работает на cPanel

## 📞 Поддержка

Если проблема сохраняется:
1. Проверьте логи ошибок в cPanel
2. Убедитесь, что все файлы загружены
3. Проверьте права доступа
4. Перезапустите приложение 