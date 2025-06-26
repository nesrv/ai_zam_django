Настроить Telegram-бота

Бот на Django можно реализовать с помощью  **Webhook**

* Это рекомендованный и более стабильный способ на хостингах с ограничениями.

#### 📌 Шаги:

1. **Создай URL-обработчик в Django**, например:

   ```python
   # urls.py
   from django.urls import path
   from . import views

   urlpatterns = [
       path('telegram-webhook/', views.telegram_webhook, name='telegram_webhook'),
   ]
   ```

2. **Создай представление (view)**:

   ```python
   import json
   import requests
   from django.views.decorators.csrf import csrf_exempt
   from django.http import JsonResponse

   TELEGRAM_TOKEN = 'your_bot_token'

   @csrf_exempt
   def telegram_webhook(request):
       if request.method == 'POST':
           data = json.loads(request.body)
           chat_id = data['message']['chat']['id']
           text = data['message'].get('text', '')

           # Пример ответа
           reply = f'Вы написали: {text}'
           url = f'https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage'
           payload = {'chat_id': chat_id, 'text': reply}
           requests.post(url, data=payload)

           return JsonResponse({'status': 'ok'})

       return JsonResponse({'status': 'only POST allowed'})
   ```

3. **Настрой Webhook через Telegram API**:
   В браузере или через curl:

   ```
   https://api.telegram.org/bot<your_bot_token>/setWebhook?url=https://yourdomain.com/telegram-webhook/
   ```

---


## 🎯 Итог

Ты можешь полностью интегрировать Django-проект с Telegram-ботом на хостинге с cPanel, используя Webhook. Это рабочее и масштабируемое решение.

Хочешь пример готового Django-приложения с Webhook?


Отлично! Ниже — **минимальный пример Django-приложения** с интеграцией Telegram-бота через **Webhook**, который можно разместить на **cPanel**.

---

## 📁 Структура проекта (пример)

```
myproject/
├── manage.py
├── myproject/
│   ├── __init__.py
│   ├── settings.py
│   ├── urls.py
│   └── wsgi.py
└── telegrambot/
    ├── __init__.py
    ├── views.py
    └── urls.py
```

---

## 1. 🧠 `settings.py` — минимальная настройка

Добавь в `INSTALLED_APPS`:

```python
INSTALLED_APPS = [
    ...
    'telegrambot',
]
```

Разреши нужный хост:

```python
ALLOWED_HOSTS = ['yourdomain.com']
```

---

## 2. 🔌 `myproject/urls.py`

```python
from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('telegram/', include('telegrambot.urls')),  # путь к Webhook
]
```

---

## 3. 📡 `telegrambot/urls.py`

```python
from django.urls import path
from .views import telegram_webhook

urlpatterns = [
    path('webhook/', telegram_webhook, name='telegram_webhook'),
]
```

---

## 4. 🤖 `telegrambot/views.py`

```python
import json
import requests
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST

TELEGRAM_TOKEN = 'your_bot_token'

@csrf_exempt
@require_POST
def telegram_webhook(request):
    try:
        data = json.loads(request.body)
        chat_id = data['message']['chat']['id']
        text = data['message'].get('text', '')

        reply = f"Вы написали: {text}"

        requests.post(
            f'https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage',
            data={'chat_id': chat_id, 'text': reply}
        )

        return JsonResponse({'ok': True})
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)
```

---

## 5. 🚀 Установка Webhook

После деплоя (на HTTPS-домене) зайди в браузере или вызови команду:

```bash
curl "https://api.telegram.org/bot<your_bot_token>/setWebhook?url=https://yourdomain.com/telegram/webhook/"
```

---

## 6. 💡 Дополнительно

* ✅ Убедись, что сайт работает по HTTPS (например, с Let's Encrypt)
* ✅ Проверь, что `/telegram/webhook/` доступен и возвращает JSON

---

## 7. Пример ответа Telegram

**Пользователь:** `Привет`

**Бот:** `Вы написали: Привет`

