from django.middleware.csrf import CsrfViewMiddleware
import logging

logger = logging.getLogger(__name__)

class CustomCsrfMiddleware(CsrfViewMiddleware):
    """Кастомный CSRF middleware с исключением для Telegram webhook"""
    
    def process_view(self, request, callback, callback_args, callback_kwargs):
        # Полностью пропускаем CSRF проверку для Telegram webhook
        if request.path == '/telegram/webhook/' and request.method == 'POST':
            logger.info("Skipping CSRF check for Telegram webhook")
            return None
        
        # Для всех остальных запросов используем стандартную CSRF проверку
        return super().process_view(request, callback, callback_args, callback_kwargs) 