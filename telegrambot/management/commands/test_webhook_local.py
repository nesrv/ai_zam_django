from django.core.management.base import BaseCommand
from django.test import Client
import json

class Command(BaseCommand):
    help = 'Тестирует webhook endpoint локально'

    def handle(self, *args, **options):
        client = Client()
        
        # Сначала тестируем доступность URL
        self.stdout.write('🔍 Проверяю доступность URL...')
        try:
            response = client.get('/telegram/webhook/')
            self.stdout.write(f'GET запрос: статус {response.status_code}')
        except Exception as e:
            self.stdout.write(f'Ошибка GET запроса: {e}')
        
        # Тестовые данные от Telegram
        test_update = {
            "update_id": 123456789,
            "message": {
                "message_id": 1,
                "from": {
                    "id": 123456789,
                    "is_bot": False,
                    "first_name": "Test",
                    "username": "testuser",
                    "language_code": "ru"
                },
                "chat": {
                    "id": 123456789,
                    "first_name": "Test",
                    "username": "testuser",
                    "type": "private"
                },
                "date": 1640995200,
                "text": "/start"
            }
        }
        
        self.stdout.write('🧪 Тестирую webhook endpoint...')
        self.stdout.write(f'📤 Отправляю данные: {json.dumps(test_update, indent=2)}')
        
        try:
            # Отправляем POST запрос к webhook
            response = client.post(
                '/telegram/webhook/',
                data=json.dumps(test_update),
                content_type='application/json',
                HTTP_USER_AGENT='TelegramBot (https://core.telegram.org/bots/api)'
            )
            
            self.stdout.write(f'📊 Статус ответа: {response.status_code}')
            self.stdout.write(f'📄 Содержимое ответа: {response.content.decode()}')
            
            if response.status_code == 200:
                self.stdout.write(
                    self.style.SUCCESS('✅ Webhook endpoint работает!')
                )
            else:
                self.stdout.write(
                    self.style.ERROR('❌ Webhook endpoint не отвечает правильно')
                )
                
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'❌ Ошибка тестирования: {e}')
            ) 