from django.core.management.base import BaseCommand
from django.utils import timezone
from datetime import timedelta
import random
from telegrambot.models import TelegramUser, TelegramMessage

class Command(BaseCommand):
    help = 'Добавляет тестовые данные для демонстрации Telegram Bot Dashboard'

    def handle(self, *args, **options):
        self.stdout.write('Добавление тестовых данных...')
        
        # Создаем тестовых пользователей
        test_users = [
            {
                'telegram_id': 123456789,
                'username': 'ivan_petrov',
                'first_name': 'Иван',
                'last_name': 'Петров'
            },
            {
                'telegram_id': 987654321,
                'username': 'maria_sidorova',
                'first_name': 'Мария',
                'last_name': 'Сидорова'
            },
            {
                'telegram_id': 555666777,
                'username': 'alex_kuznetsov',
                'first_name': 'Алексей',
                'last_name': 'Кузнецов'
            },
            {
                'telegram_id': 111222333,
                'username': 'anna_ivanova',
                'first_name': 'Анна',
                'last_name': 'Иванова'
            },
            {
                'telegram_id': 444555666,
                'username': 'dmitry_smirnov',
                'first_name': 'Дмитрий',
                'last_name': 'Смирнов'
            }
        ]
        
        created_users = []
        for user_data in test_users:
            user, created = TelegramUser.objects.get_or_create(
                telegram_id=user_data['telegram_id'],
                defaults=user_data
            )
            if created:
                self.stdout.write(f'Создан пользователь: {user.first_name} (@{user.username})')
            created_users.append(user)
        
        # Создаем тестовые сообщения за последние 7 дней
        messages_data = [
            # Иван Петров - активный пользователь
            ('/start', 'command', True),
            ('Привет! Я тестовый бот. Напиши что-нибудь!', 'text', False),
            ('Привет', 'text', True),
            ('Привет! Как дела?', 'text', False),
            ('Хорошо, спасибо!', 'text', True),
            ('Отлично! Рад это слышать.', 'text', False),
            ('/help', 'command', True),
            ('Доступные команды:\n/start - начать общение\n/help - помощь', 'text', False),
            
            # Мария Сидорова
            ('/start', 'command', True),
            ('Привет! Я тестовый бот. Напиши что-нибудь!', 'text', False),
            ('Здравствуйте', 'text', True),
            ('Здравствуйте! Как дела?', 'text', False),
            
            # Алексей Кузнецов
            ('/start', 'command', True),
            ('Привет! Я тестовый бот. Напиши что-нибудь!', 'text', False),
            ('Пока', 'text', True),
            ('До свидания! Возвращайся :)', 'text', False),
            
            # Анна Иванова
            ('/start', 'command', True),
            ('Привет! Я тестовый бот. Напиши что-нибудь!', 'text', False),
            ('Как дела?', 'text', True),
            ('Отлично! Спасибо что спросили.', 'text', False),
            
            # Дмитрий Смирнов
            ('/start', 'command', True),
            ('Привет! Я тестовый бот. Напиши что-нибудь!', 'text', False),
            ('Тест', 'text', True),
            ('Я не понял сообщение. Попробуй /help', 'text', False),
        ]
        
        # Создаем сообщения с разными временными метками
        base_time = timezone.now()
        message_count = 0
        
        for user in created_users:
            # Каждый пользователь получает несколько сообщений
            for i, (content, msg_type, is_from_user) in enumerate(messages_data[:8]):  # Первые 8 сообщений для каждого
                # Создаем временную метку в пределах последних 7 дней
                time_offset = timedelta(
                    days=random.randint(0, 7),
                    hours=random.randint(0, 23),
                    minutes=random.randint(0, 59)
                )
                created_at = base_time - time_offset
                
                TelegramMessage.objects.create(
                    user=user,
                    content=content,
                    message_type=msg_type,
                    is_from_user=is_from_user,
                    created_at=created_at
                )
                message_count += 1
        
        self.stdout.write(
            self.style.SUCCESS(
                f'Успешно добавлено {len(created_users)} пользователей и {message_count} сообщений!'
            )
        )
        self.stdout.write('Теперь вы можете посмотреть dashboard на http://127.0.0.1:8000/telegram/') 