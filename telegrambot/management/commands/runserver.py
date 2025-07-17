import os
import threading
import time
import logging
from django.core.management.base import BaseCommand
from django.core.management import call_command

logger = logging.getLogger(__name__)

class Command(BaseCommand):
    """
    Переопределение стандартной команды runserver для запуска с поллером Telegram
    """
    
    help = 'Запускает Django сервер вместе с поллером Telegram'

    def add_arguments(self, parser):
        # Добавляем аргументы стандартной команды runserver
        parser.add_argument(
            'addrport',
            nargs='?',
            help='Optional port number, or ipaddr:port',
        )
        parser.add_argument(
            '--ipv6', '-6',
            action='store_true',
            help='Tells Django to use an IPv6 address.',
        )
        parser.add_argument(
            '--nothreading',
            action='store_true',
            help='Tells Django to NOT use threading.',
        )
        parser.add_argument(
            '--noreload',
            action='store_true',
            help='Tells Django to NOT use the auto-reloader.',
        )
        parser.add_argument(
            '--nostatic',
            action='store_true',
            help='Tells Django to NOT automatically serve static files at STATIC_URL.',
        )
        parser.add_argument(
            '--insecure',
            action='store_true',
            help='Allows serving static files even if DEBUG is False.',
        )
        
        # Добавляем аргументы для поллера
        parser.add_argument(
            '--no-poller',
            action='store_true',
            help='Запустить только Django сервер без поллера Telegram',
        )
        parser.add_argument(
            '--poll-interval',
            type=int,
            default=5,
            help='Интервал опроса Telegram API в секундах (по умолчанию 5)',
        )

    def handle(self, *args, **options):
        # Извлекаем аргументы для поллера
        no_poller = options.pop('no_poller', False)
        interval = options.pop('poll_interval', 5)
        
        # Если не указан флаг --no-poller, запускаем runserver_with_poller
        if not no_poller:
            self.stdout.write(self.style.SUCCESS('Запускаем Django сервер с поллером Telegram...'))
            
            # Формируем аргументы для runserver_with_poller
            poller_args = []
            if options.get('addrport'):
                poller_args.append(options['addrport'])
            
            # Добавляем интервал опроса
            poller_args.append(f'--interval={interval}')
            
            # Запускаем runserver_with_poller
            call_command('runserver_with_poller', *poller_args)
        else:
            # Если указан флаг --no-poller, запускаем стандартную команду runserver
            self.stdout.write(self.style.SUCCESS('Запускаем Django сервер без поллера Telegram...'))
            
            # Формируем аргументы для стандартной команды runserver
            runserver_args = []
            if options.get('addrport'):
                runserver_args.append(options['addrport'])
            
            # Запускаем стандартную команду Django runserver
            from django.core.management.commands.runserver import Command as RunserverCommand
            runserver_cmd = RunserverCommand()
            runserver_cmd.handle(*runserver_args, **options)