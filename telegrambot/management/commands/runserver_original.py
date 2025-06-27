from django.core.management.base import BaseCommand
from django.core.management import call_command
import threading
import time
import sys
import os

class Command(BaseCommand):
    help = 'Запускает Django сервер вместе с Telegram ботами (оригинальная команда)'

    def add_arguments(self, parser):
        parser.add_argument(
            '--host',
            default='127.0.0.1',
            help='Хост для запуска сервера (по умолчанию: 127.0.0.1)'
        )
        parser.add_argument(
            '--port',
            default='8000',
            help='Порт для запуска сервера (по умолчанию: 8000)'
        )
        parser.add_argument(
            '--no-bots',
            action='store_true',
            help='НЕ запускать ботов (только сервер)'
        )

    def handle(self, *args, **options):
        host = options['host']
        port = options['port']
        no_bots = options['no_bots']
        
        self.stdout.write(
            self.style.SUCCESS(f'🚀 Запускаю Django сервер на {host}:{port}')
        )
        
        if not no_bots:
            self.stdout.write(
                self.style.SUCCESS('🤖 Запускаю Telegram боты в фоновом режиме...')
            )
            
            # Запускаем боты в отдельном потоке
            def run_bots_thread():
                try:
                    # Импортируем и запускаем ботов
                    from telegrambot.bot_integrated import start_bots
                    start_bots()
                except Exception as e:
                    self.stdout.write(
                        self.style.ERROR(f'❌ Ошибка запуска ботов: {e}')
                    )
            
            bot_thread = threading.Thread(target=run_bots_thread, daemon=True)
            bot_thread.start()
            
            self.stdout.write(
                self.style.SUCCESS('✅ Боты запущены в фоновом режиме')
            )
        else:
            self.stdout.write(
                self.style.WARNING('⚠️ Боты отключены (используйте --no-bots для отключения)')
            )
        
        # Запускаем Django сервер
        try:
            from django.core.management.commands.runserver import Command as RunserverCommand
            runserver_cmd = RunserverCommand()
            runserver_cmd.handle(f'{host}:{port}', verbosity=1)
        except KeyboardInterrupt:
            self.stdout.write(
                self.style.WARNING('\n🛑 Сервер остановлен пользователем')
            )
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'❌ Ошибка запуска сервера: {e}')
            ) 