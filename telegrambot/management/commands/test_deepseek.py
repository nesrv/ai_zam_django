from django.core.management.base import BaseCommand
from telegrambot.services import generate_document_with_deepseek

class Command(BaseCommand):
    help = 'Тестирует подключение к DeepSeek API'

    def handle(self, *args, **options):
        self.stdout.write('🧪 Тестирую подключение к DeepSeek API...')
        
        # Тестовый промпт
        test_prompt = "Составь лимитно-заборную карту (ЛЗК) на бетон М300, арматура А500С, опалубка щитовая"
        
        try:
            result = generate_document_with_deepseek(test_prompt)
            
            if result.startswith('Ошибка'):
                self.stdout.write(self.style.ERROR(f'❌ Ошибка: {result}'))
            else:
                self.stdout.write(self.style.SUCCESS('✅ DeepSeek API работает!'))
                self.stdout.write(f'📄 Сгенерированный документ:\n{result[:500]}...')
                
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'❌ Исключение: {str(e)}')) 