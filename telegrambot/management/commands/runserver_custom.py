from django.core.management.base import BaseCommand
from django.core.management import call_command
import sys

class Command(BaseCommand):
    help = 'Запускает сервер разработки с ботами (переопределяет стандартную команду runserver)'

    def add_arguments(self, parser):
        # Добавляем наш кастомный аргумент
        parser.add_argument(
            '--no-bots',
            action='store_true',
            help='Запустить сервер без ботов',
        )
        # Добавляем аргументы, которые поддерживает стандартная команда runserver
        parser.add_argument(
            'addrport',
            nargs='?',
            help='Порт для запуска сервера (например: 8000 или 127.0.0.1:8000)',
        )
        parser.add_argument(
            '--noreload',
            action='store_true',
            help='Не перезагружать сервер при изменении файлов',
        )
        parser.add_argument(
            '--nothreading',
            action='store_true',
            help='Не использовать многопоточность',
        )
        parser.add_argument(
            '--ipv6',
            '-6',
            action='store_true',
            help='Использовать IPv6',
        )
        parser.add_argument(
            '--nostatic',
            action='store_true',
            help='Не обслуживать статические файлы',
        )
        parser.add_argument(
            '--insecure',
            action='store_true',
            help='Разрешить обслуживание статических файлов даже если DEBUG=False',
        )

    def handle(self, *args, **options):
        # Извлекаем наш кастомный аргумент
        no_bots = options.pop('no_bots', False)
        
        if no_bots:
            # Если указан флаг --no-bots, запускаем стандартную команду runserver
            self.stdout.write('🚫 Запуск сервера без ботов...')
            # Создаем список аргументов для стандартной команды
            runserver_args = []
            if options.get('addrport'):
                runserver_args.append(options['addrport'])
            
            # Запускаем стандартную команду Django runserver
            from django.core.management.commands.runserver import Command as RunserverCommand
            runserver_cmd = RunserverCommand()
            runserver_cmd.handle(*runserver_args, **options)
        else:
            # Иначе запускаем runserver_with_bots
            self.stdout.write('🤖 Запуск сервера с ботами...')
            call_command('runserver_with_bots', *args, **options) 