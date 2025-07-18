import os
import logging
from django.core.management.base import BaseCommand
from telegrambot.telegram_poller import remove_lock_file
from telegrambot.models import ProcessedUpdate

logger = logging.getLogger(__name__)

class Command(BaseCommand):
    help = 'Сбрасывает состояние поллера Telegram, удаляет файлы блокировки и очищает таблицу обработанных обновлений'

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('Начинаем сброс состояния поллера Telegram...'))
        
        # Удаляем файлы блокировки
        removed = remove_lock_file()
        if removed:
            self.stdout.write(self.style.SUCCESS('Файлы блокировки успешно удалены'))
        else:
            self.stdout.write(self.style.WARNING('Не удалось удалить файлы блокировки или они не существуют'))
        
        # Очищаем таблицу обработанных обновлений
        try:
            count = ProcessedUpdate.objects.all().count()
            ProcessedUpdate.objects.all().delete()
            self.stdout.write(self.style.SUCCESS(f'Удалено {count} записей из таблицы обработанных обновлений'))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'Ошибка при очистке таблицы обработанных обновлений: {e}'))
        
        # Сбрасываем вебхук Telegram
        try:
            import requests
            from django.conf import settings
            
            token = os.getenv('TELEGRAM_TOKEN')
            if token:
                url = f"https://api.telegram.org/bot{token}/deleteWebhook?drop_pending_updates=true"
                response = requests.get(url, timeout=5)
                if response.status_code == 200:
                    self.stdout.write(self.style.SUCCESS('Вебхук Telegram успешно сброшен'))
                else:
                    self.stdout.write(self.style.WARNING(f'Ошибка сброса вебхука: {response.status_code} - {response.text}'))
            else:
                self.stdout.write(self.style.WARNING('Токен Telegram не найден в переменных окружения'))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'Ошибка при сбросе вебхука: {e}'))
        
        self.stdout.write(self.style.SUCCESS('Сброс состояния поллера Telegram завершен'))