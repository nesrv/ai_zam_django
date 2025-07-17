#!/usr/bin/env python
"""Django's command-line utility for administrative tasks."""
import os
import sys


def main():
    """Run administrative tasks."""
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ai_zam.settings')
    try:
        from django.core.management import execute_from_command_line
    except ImportError as exc:
        raise ImportError(
            "Couldn't import Django. Are you sure it's installed and "
            "available on your PYTHONPATH environment variable? Did you "
            "forget to activate a virtual environment?"
        ) from exc
    
    # Заменяем команду runserver на runserver_with_poller
    if len(sys.argv) > 1 and sys.argv[1] == 'runserver' and '--no-poller' not in sys.argv:
        # Заменяем 'runserver' на 'runserver_with_poller'
        sys.argv[1] = 'runserver_with_poller'
        print('\033[32m[OK] Запускаем Django сервер с поллером Telegram...\033[0m')
    
    execute_from_command_line(sys.argv)


if __name__ == '__main__':
    main()
