#!/usr/bin/env python
"""
Скрипт для сборки статических файлов на продакшене
"""
import os
import django
from django.core.management import execute_from_command_line

if __name__ == '__main__':
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ai_zam.settings')
    django.setup()
    
    print("Собираем статические файлы...")
    execute_from_command_line(['manage.py', 'collectstatic', '--noinput'])
    print("Статические файлы собраны успешно!")