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
CSRF_HEADER_NAME = 'HTTP_X_CSRFTOKEN'
```

### 3. Улучшенное логирование

Webhook теперь логирует:

- IP адрес запроса
- User-Agent
- Успешные/неуспешные обработки
- Подозрительные запросы

## 🚨 Новая проблема: nginx 403 Forbidden

После решения проблемы с Referer может появиться новая ошибка:

```
403 Forbidden
nginx/1.20.1
```

### Решение проблемы с nginx

#### 1. Создайте файл .htaccess в корне сайта

```apache
# Настройки для Django
RewriteEngine On
RewriteCond %{REQUEST_FILENAME} !-f
RewriteRule ^(.*)$ /index.py/$1 [QSA,L]

# Разрешаем запросы к webhook
<Location "/telegram/webhook/">
    Require all granted
    Allow from all
</Location>

# Настройки для nginx (если используется)
<IfModule mod_headers.c>
    Header always set Access-Control-Allow-Origin "*"
    Header always set Access-Control-Allow-Methods "GET, POST, OPTIONS"
    Header always set Access-Control-Allow-Headers "Content-Type, Authorization"
</IfModule>

# Разрешаем POST запросы к webhook
<LocationMatch "^/telegram/webhook/">
    Require all granted
    Allow from all
    <LimitExcept GET POST OPTIONS>
        Deny from all
    </LimitExcept>
</LocationMatch>
```

#### 2. Настройка nginx в cPanel

1. Войдите в cPanel
2. Найдите раздел **Domains** → **Domains**
3. Нажмите **Manage** рядом с вашим доменом
4. В разделе **Web Server Configuration** выберите **nginx**
5. Добавьте в конфигурацию nginx:

```nginx
# Специальные настройки для Telegram webhook
location /telegram/webhook/ {
    # Разрешаем все запросы от Telegram
    allow all;
  
    # Настройки для POST запросов
    if ($request_method = POST) {
        proxy_pass http://127.0.0.1:8000;  # Замените на порт вашего Django
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
  
    # Настройки для GET запросов (статус)
    if ($request_method = GET) {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
  
    # Разрешаем OPTIONS для CORS
    if ($request_method = OPTIONS) {
        add_header Access-Control-Allow-Origin "*";
        add_header Access-Control-Allow-Methods "GET, POST, OPTIONS";
        add_header Access-Control-Allow-Headers "Content-Type, Authorization";
        return 200;
    }
}
```

#### 3. Альтернативное решение через cPanel

1. В cPanel найдите **Security** → **IP Blocker**
2. Убедитесь, что IP адреса Telegram не заблокированы
3. В **Security** → **ModSecurity** временно отключите для тестирования
4. В **Security** → **Hotlink Protection** добавьте исключение для `/telegram/webhook/`

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
curl "https://api.telegram.org/bot7606767600:AAFGN18TMl0pUQIsQzaKiozmMKe0KBeSjyE/getWebhookInfo"
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
- ✅ Нет ошибок "nginx 403 Forbidden"
- ✅ Улучшенное логирование для отладки
- ✅ Сохранена безопасность
- ✅ Работает на cPanel

## 📞 Поддержка

Если проблема сохраняется:

1. Проверьте логи ошибок в cPanel
2. Убедитесь, что все файлы загружены
3. Проверьте права доступа
4. Перезапустите приложение
5. Проверьте настройки nginx в cPanel
