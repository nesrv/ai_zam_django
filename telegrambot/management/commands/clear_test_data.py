from django.core.management.base import BaseCommand
from telegrambot.models import TelegramUser, TelegramMessage

class Command(BaseCommand):
    help = 'Очищает тестовые данные из базы'

    def add_arguments(self, parser):
        parser.add_argument(
            '--confirm',
            action='store_true',
            help='Подтвердить удаление',
        )

    def handle(self, *args, **options):
        if not options['confirm']:
            self.stdout.write(
                self.style.WARNING(
                    '⚠️ Это удалит ВСЕ тестовые данные! Используйте --confirm для подтверждения.'
                )
            )
            return
        
        # Удаляем все тестовые сообщения
        messages_count = TelegramMessage.objects.count()
        TelegramMessage.objects.all().delete()
        
        # Удаляем всех тестовых пользователей
        users_count = TelegramUser.objects.count()
        TelegramUser.objects.all().delete()
        
        self.stdout.write(
            self.style.SUCCESS(
                f'✅ Удалено {users_count} пользователей и {messages_count} сообщений'
            )
        )
        self.stdout.write('Теперь база данных пуста. Добавьте реальных пользователей через Telegram бота.') 