import os
import sys
import django
import asyncio
import logging
from django.core.management.base import BaseCommand
from django.conf import settings
from django.db import connection
from telegrambot.bot_integrated import main as bot_main, validate_config

logger = logging.getLogger(__name__)

class Command(BaseCommand):
    help = 'Запускает Telegram бота в фоновом режиме с Django'

    def add_arguments(self, parser):
        parser.add_argument(
            '--daemon',
            action='store_true',
            help='Запустить в режиме демона (фоновый процесс)',
        )
        parser.add_argument(
            '--webhook',
            action='store_true',
            help='Использовать webhook вместо polling',
        )

    def handle(self, *args, **options):
        # Настройка Django
        os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ai_zam.settings')
        django.setup()
        
        self.stdout.write(
            self.style.SUCCESS('🚀 Запуск Telegram бота с Django...')
        )
        
        # Проверяем конфигурацию
        if not validate_config():
            self.stdout.write(
                self.style.ERROR('❌ Ошибка конфигурации бота')
            )
            sys.exit(1)
        
        try:
            # Закрываем соединения с БД перед запуском бота
            connection.close()
            
            if options['daemon']:
                self.stdout.write('🔄 Запуск в режиме демона...')
                # Здесь можно добавить логику для запуска в фоне
                # Например, через systemd или supervisor
                pass
            
            if options['webhook']:
                self.stdout.write('🌐 Использование webhook режима...')
                # Логика для webhook будет в отдельной команде
                pass
            
            # Запускаем бота
            self.stdout.write('🤖 Запуск бота...')
            bot_main()
            
        except KeyboardInterrupt:
            self.stdout.write(
                self.style.WARNING('\n⚠️ Бот остановлен пользователем')
            )
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'❌ Ошибка запуска бота: {e}')
            )
            logger.error(f"Ошибка запуска бота: {e}")
            sys.exit(1) 