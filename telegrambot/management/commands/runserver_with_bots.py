import threading
import time
import logging
from django.core.management.base import BaseCommand
from django.core.management import call_command
from django.conf import settings

logger = logging.getLogger(__name__)

class Command(BaseCommand):
    help = 'Запускает Django сервер вместе с Telegram ботами'

    def add_arguments(self, parser):
        parser.add_argument(
            '--bots-only',
            action='store_true',
            help='Запустить только боты без Django сервера',
        )
        parser.add_argument(
            '--django-only',
            action='store_true',
            help='Запустить только Django сервер без ботов',
        )

    def handle(self, *args, **options):
        bots_only = options.get('bots_only', False)
        django_only = options.get('django_only', False)
        
        if bots_only:
            self.stdout.write(
                self.style.SUCCESS('Запуск только Telegram ботов...')
            )
            self._start_bots()
        elif django_only:
            self.stdout.write(
                self.style.SUCCESS('Запуск только Django сервера...')
            )
            self._start_django_server()
        else:
            self.stdout.write(
                self.style.SUCCESS('Запуск Django сервера с Telegram ботами...')
            )
            self._start_django_with_bots()

    def _start_bots(self):
        """Запускает только интегрированный бот"""
        try:
            from telegrambot.bot_integrated import main
            
            self.stdout.write(
                self.style.SUCCESS('Инициализация интегрированного Telegram бота...')
            )
            
            # Запускаем интегрированный бот
            main()
            
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'Ошибка запуска бота: {e}')
            )

    def _start_django_server(self):
        """Запускает только Django сервер"""
        try:
            call_command('runserver')
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'Ошибка запуска Django сервера: {e}')
            )

    def _start_django_with_bots(self):
        """Запускает Django сервер и интегрированный бот одновременно"""
        try:
            # Запускаем бота в отдельном потоке
            def run_bot():
                from telegrambot.bot_integrated import main
                main()
            
            self.stdout.write(
                self.style.SUCCESS('Инициализация интегрированного Telegram бота...')
            )
            
            bot_thread = threading.Thread(target=run_bot, daemon=True)
            bot_thread.start()
            
            self.stdout.write(
                self.style.SUCCESS('✅ Интегрированный бот запущен')
            )
            
            # Небольшая задержка для инициализации бота
            time.sleep(3)
            
            self.stdout.write(
                self.style.SUCCESS('Запуск Django сервера...')
            )
            
            # Запускаем Django сервер
            call_command('runserver')
            
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'Ошибка: {e}')
            ) 