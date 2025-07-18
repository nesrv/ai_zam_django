import os
import sys
import threading
import time
import logging
from django.core.management.base import BaseCommand
from django.core.management import call_command
from telegrambot.telegram_poller import TelegramPoller

logger = logging.getLogger(__name__)

class Command(BaseCommand):
    help = 'Запускает Django сервер вместе с поллером Telegram'

    def add_arguments(self, parser):
        parser.add_argument(
            '--django-only',
            action='store_true',
            help='Запустить только Django сервер без поллера',
        )
        parser.add_argument(
            '--poller-only',
            action='store_true',
            help='Запустить только поллер без Django сервера',
        )
        parser.add_argument(
            '--interval',
            type=int,
            default=10,
            help='Интервал опроса Telegram API в секундах (по умолчанию 5)',
        )

    def handle(self, *args, **options):
        django_only = options.get('django_only', False)
        poller_only = options.get('poller_only', False)
        interval = options.get('interval', 20)

        # Запускаем поллер, если не указан флаг django-only
        poller = None
        if not django_only:
            self.stdout.write(self.style.SUCCESS('Запускаем поллер Telegram...'))
            token = os.getenv('TELEGRAM_TOKEN')
            if not token:
                self.stdout.write(self.style.ERROR('Не найден токен Telegram! Проверьте .env файл'))
                return
            
            poller = TelegramPoller(token=token, interval=interval)
            poller_started = poller.start()
            
            if poller_started:
                self.stdout.write(self.style.SUCCESS(f'Поллер Telegram запущен с интервалом {interval} сек.'))
            else:
                self.stdout.write(self.style.ERROR('Не удалось запустить поллер Telegram'))
                return
        
        # Запускаем Django сервер, если не указан флаг poller-only
        if not poller_only:
            self.stdout.write(self.style.SUCCESS('Запускаем Django сервер...'))
            try:
                # Запускаем стандартную команду runserver
                call_command('runserver')
            except KeyboardInterrupt:
                self.stdout.write(self.style.SUCCESS('Django сервер остановлен'))
            except Exception as e:
                self.stdout.write(self.style.ERROR(f'Ошибка запуска Django сервера: {e}'))
        else:
            # Если запущен только поллер, ждем прерывания
            self.stdout.write(self.style.SUCCESS('Поллер запущен. Нажмите Ctrl+C для остановки.'))
            try:
                while True:
                    time.sleep(1)
            except KeyboardInterrupt:
                self.stdout.write(self.style.SUCCESS('Получен сигнал остановки'))
        
        # Останавливаем поллер при выходе
        if poller:
            self.stdout.write(self.style.SUCCESS('Останавливаем поллер Telegram...'))
            poller.stop()
            self.stdout.write(self.style.SUCCESS('Поллер Telegram остановлен'))