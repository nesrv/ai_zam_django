from django.core.management.base import BaseCommand
from telegrambot.services import BOT_TOKEN
import requests
import json

class Command(BaseCommand):
    help = 'Тестирует webhook и получение сообщений из Telegram'

    def add_arguments(self, parser):
        parser.add_argument(
            '--set-webhook',
            action='store_true',
            help='Установить webhook'
        )
        parser.add_argument(
            '--delete-webhook',
            action='store_true',
            help='Удалить webhook'
        )
        parser.add_argument(
            '--get-updates',
            action='store_true',
            help='Получить обновления'
        )
        parser.add_argument(
            '--get-webhook-info',
            action='store_true',
            help='Получить информацию о webhook'
        )

    def handle(self, *args, **options):
        if not BOT_TOKEN:
            self.stdout.write(self.style.ERROR('❌ Токен бота не найден!'))
            return

        if options['set_webhook']:
            self.set_webhook()
        elif options['delete_webhook']:
            self.delete_webhook()
        elif options['get_updates']:
            self.get_updates()
        elif options['get_webhook_info']:
            self.get_webhook_info()
        else:
            self.show_help()

    def set_webhook(self):
        """Устанавливает webhook"""
        webhook_url = "https://programism.ru/telegram/webhook/"
        
        try:
            response = requests.post(
                f"https://api.telegram.org/bot{BOT_TOKEN}/setWebhook",
                json={'url': webhook_url}
            )
            
            if response.status_code == 200:
                result = response.json()
                if result.get('ok'):
                    self.stdout.write(
                        self.style.SUCCESS(f'✅ Webhook установлен: {webhook_url}')
                    )
                else:
                    self.stdout.write(
                        self.style.ERROR(f'❌ Ошибка установки webhook: {result}')
                    )
            else:
                self.stdout.write(
                    self.style.ERROR(f'❌ HTTP ошибка: {response.status_code}')
                )
                
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'❌ Ошибка: {e}')
            )

    def delete_webhook(self):
        """Удаляет webhook"""
        try:
            response = requests.post(
                f"https://api.telegram.org/bot{BOT_TOKEN}/deleteWebhook"
            )
            
            if response.status_code == 200:
                result = response.json()
                if result.get('ok'):
                    self.stdout.write(
                        self.style.SUCCESS('✅ Webhook удален')
                    )
                else:
                    self.stdout.write(
                        self.style.ERROR(f'❌ Ошибка удаления webhook: {result}')
                    )
            else:
                self.stdout.write(
                    self.style.ERROR(f'❌ HTTP ошибка: {response.status_code}')
                )
                
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'❌ Ошибка: {e}')
            )

    def get_updates(self):
        """Получает обновления"""
        try:
            response = requests.get(
                f"https://api.telegram.org/bot{BOT_TOKEN}/getUpdates"
            )
            
            if response.status_code == 200:
                result = response.json()
                if result.get('ok'):
                    updates = result.get('result', [])
                    if updates:
                        self.stdout.write(
                            self.style.SUCCESS(f'📨 Получено {len(updates)} обновлений:')
                        )
                        for update in updates:
                            self.stdout.write(f'  - {update}')
                    else:
                        self.stdout.write(
                            self.style.WARNING('⚠️ Обновлений нет')
                        )
                else:
                    self.stdout.write(
                        self.style.ERROR(f'❌ Ошибка получения обновлений: {result}')
                    )
            else:
                self.stdout.write(
                    self.style.ERROR(f'❌ HTTP ошибка: {response.status_code}')
                )
                
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'❌ Ошибка: {e}')
            )

    def get_webhook_info(self):
        """Получает информацию о webhook"""
        try:
            response = requests.get(
                f"https://api.telegram.org/bot{BOT_TOKEN}/getWebhookInfo"
            )
            
            if response.status_code == 200:
                result = response.json()
                if result.get('ok'):
                    info = result.get('result', {})
                    self.stdout.write(
                        self.style.SUCCESS('📋 Информация о webhook:')
                    )
                    self.stdout.write(f'  URL: {info.get("url", "Не установлен")}')
                    self.stdout.write(f'  Ошибки: {info.get("last_error_message", "Нет")}')
                    self.stdout.write(f'  Последняя ошибка: {info.get("last_error_date", "Нет")}')
                    self.stdout.write(f'  Обновлений: {info.get("pending_update_count", 0)}')
                else:
                    self.stdout.write(
                        self.style.ERROR(f'❌ Ошибка получения информации: {result}')
                    )
            else:
                self.stdout.write(
                    self.style.ERROR(f'❌ HTTP ошибка: {response.status_code}')
                )
                
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'❌ Ошибка: {e}')
            )

    def show_help(self):
        """Показывает справку"""
        self.stdout.write(
            self.style.SUCCESS('🔧 Команды для работы с webhook:')
        )
        self.stdout.write('  python manage.py test_webhook --set-webhook')
        self.stdout.write('  python manage.py test_webhook --delete-webhook')
        self.stdout.write('  python manage.py test_webhook --get-updates') 