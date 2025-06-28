from django.core.management.base import BaseCommand
from django.core.cache import cache
from django.conf import settings
import os
import shutil

class Command(BaseCommand):
    help = 'Очищает весь кэш Django и пересобирает статические файлы'

    def add_arguments(self, parser):
        parser.add_argument(
            '--static-only',
            action='store_true',
            help='Только пересобрать статические файлы',
        )
        parser.add_argument(
            '--cache-only',
            action='store_true',
            help='Только очистить кэш',
        )

    def handle(self, *args, **options):
        if not options['static_only']:
            self.stdout.write('🧹 Очищаю кэш Django...')
            cache.clear()
            self.stdout.write(self.style.SUCCESS('✅ Кэш очищен'))
        
        if not options['cache_only']:
            self.stdout.write('📁 Пересобираю статические файлы...')
            
            # Удаляем старую папку staticfiles
            staticfiles_dir = settings.STATIC_ROOT
            if os.path.exists(staticfiles_dir):
                shutil.rmtree(staticfiles_dir)
                self.stdout.write(f'🗑️ Удалена папка {staticfiles_dir}')
            
            # Пересобираем статические файлы
            from django.core.management import call_command
            call_command('collectstatic', '--noinput')
            self.stdout.write(self.style.SUCCESS('✅ Статические файлы пересобраны'))
        
        self.stdout.write(self.style.SUCCESS('🎉 Очистка завершена! Перезапустите сервер для применения изменений.')) 