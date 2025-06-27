from django.core.management.base import BaseCommand
from telegrambot.services import check_bot_token, send_telegram_message, BOT_TOKEN
from telegrambot.models import TelegramUser

class Command(BaseCommand):
    help = 'Тестирует бота и отправляет тестовое сообщение'

    def add_arguments(self, parser):
        parser.add_argument(
            '--test-token',
            action='store_true',
            help='Проверить токен бота',
        )
        parser.add_argument(
            '--send-test',
            action='store_true',
            help='Отправить тестовое сообщение первому пользователю',
        )

    def handle(self, *args, **options):
        if options['test_token']:
            self.stdout.write('Проверка токена бота...')
            is_valid, bot_info = check_bot_token(BOT_TOKEN)
            if is_valid:
                self.stdout.write(
                    self.style.SUCCESS(f'✅ Токен валиден! Бот: {bot_info.get("first_name")} (@{bot_info.get("username")})')
                )
            else:
                self.stdout.write(
                    self.style.ERROR(f'❌ Токен недействителен: {bot_info}')
                )
        
        if options['send_test']:
            self.stdout.write('Отправка тестового сообщения...')
            
            # Проверяем токен
            is_valid, bot_info = check_bot_token(BOT_TOKEN)
            if not is_valid:
                self.stdout.write(
                    self.style.ERROR(f'❌ Токен недействителен: {bot_info}')
                )
                return
            
            # Получаем первого активного пользователя
            user = TelegramUser.objects.filter(is_active=True).first()
            if not user:
                self.stdout.write(
                    self.style.WARNING('⚠️ Нет активных пользователей для тестирования')
                )
                return
            
            self.stdout.write(f'Отправка сообщения пользователю {user.telegram_id} ({user.first_name})...')
            
            # Отправляем тестовое сообщение
            result = send_telegram_message(user.telegram_id, "🧪 Тестовое сообщение от AI-ZAM бота!")
            
            if result and result.get('ok'):
                self.stdout.write(
                    self.style.SUCCESS(f'✅ Сообщение успешно отправлено!')
                )
            else:
                self.stdout.write(
                    self.style.ERROR(f'❌ Ошибка отправки: {result}')
                )
        
        if not options['test_token'] and not options['send_test']:
            self.stdout.write('Использование:')
            self.stdout.write('  python manage.py test_bot --test-token')
            self.stdout.write('  python manage.py test_bot --send-test') 