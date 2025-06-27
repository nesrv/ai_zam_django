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
        """Запускает только ne_srv_bot"""
        try:
            from telegrambot.services import start_all_bots
            
            self.stdout.write(
                self.style.SUCCESS('Инициализация Telegram бота...')
            )
            
            bot_thread = start_all_bots()
            
            self.stdout.write(
                self.style.SUCCESS('✅ NE_SRV_BOT запущен')
            )
            
            # Держим бота запущенным
            try:
                while True:
                    time.sleep(1)
            except KeyboardInterrupt:
                self.stdout.write(
                    self.style.WARNING('Остановка бота...')
                )
                
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
        """Запускает Django сервер и ne_srv_bot одновременно"""
        try:
            # Запускаем бота в отдельном потоке
            from telegrambot.services import start_all_bots
            
            self.stdout.write(
                self.style.SUCCESS('Инициализация Telegram бота...')
            )
            
            bot_thread = start_all_bots()
            
            self.stdout.write(
                self.style.SUCCESS('✅ NE_SRV_BOT запущен')
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