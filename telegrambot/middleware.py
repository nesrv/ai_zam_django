import logging
from django.conf import settings

logger = logging.getLogger(__name__)

class TelegramWebhookMiddleware:
    """Middleware для обработки Telegram webhook без проверки Referer"""
    
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Проверяем, является ли это запросом к Telegram webhook
        if request.path == '/telegram/webhook/' and request.method == 'POST':
            # Принудительно устанавливаем Referer для Telegram webhook
            request.META['HTTP_REFERER'] = 'https://api.telegram.org'
            
            # Отключаем CSRF проверку для этого запроса
            request._dont_enforce_csrf_checks = True
            
            logger.info("Telegram webhook request detected, bypassing Referer and CSRF checks")
        
        response = self.get_response(request)
        return response 