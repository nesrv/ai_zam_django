#!/usr/bin/env python
"""
Скрипт для очистки кэша шаблонов Django
"""
import os
import sys
import django

# Настройка путей для Django
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ai_zam.settings')

# Инициализация Django
django.setup()

from django.template.loader import get_template
from django.template import engines

def clear_template_cache():
    """Очистка кэша шаблонов Django"""
    print("Очистка кэша шаблонов...")
    
    # Получаем движок шаблонов Django
    django_engine = engines['django']
    
    # Очищаем кэш шаблонов
    if hasattr(django_engine, 'template_loaders'):
        for loader in django_engine.template_loaders:
            if hasattr(loader, 'reset'):
                loader.reset()
            elif hasattr(loader, 'get_template_cache'):
                loader.get_template_cache.clear()
    
    # Пытаемся очистить кэш конкретного шаблона
    try:
        template = get_template('analytics/legal_risks.html')
        if hasattr(template, 'template') and hasattr(template.template, 'nodelist'):
            template.template.nodelist = None
    except Exception as e:
        print(f"Ошибка при очистке кэша шаблона: {e}")
    
    print("Кэш шаблонов очищен.")

if __name__ == "__main__":
    clear_template_cache()
    print("Перезапустите сервер Django для применения изменений.")