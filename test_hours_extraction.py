#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Тестовый скрипт для проверки извлечения часов из сообщений
"""

import re

def extract_hours_from_message(message_content):
    """Извлекает часы из сообщения по тому же алгоритму, что и в views.py"""
    hours_data = {}
    
    if message_content:
        print(f"Анализируем текст: {message_content}")
        
        # Ищем паттерны "Фамилия число" в сообщении с учетом различных форматов
        patterns = [
            r'([А-Яа-яЁё]+)\s+(\d{1,2})(?:\s|$)',  # Фамилия пробел число
            r'([А-Яа-яЁё]+)\s*-\s*(\d{1,2})',      # Фамилия тире число
            r'([А-Яа-яЁё]+)\s*:\s*(\d{1,2})',      # Фамилия двоеточие число
            r'([А-Яа-яЁё]+)\s*=\s*(\d{1,2})',      # Фамилия равно число
            r'([А-Яа-яЁё]+)\s*(\d{1,2})',          # Фамилия число (без разделителя)
        ]
        
        for pattern in patterns:
            matches = re.findall(pattern, message_content)
            for surname, hours in matches:
                # Проверяем, что часы в разумных пределах (1-24)
                try:
                    hours_int = int(hours)
                    if 1 <= hours_int <= 24:
                        hours_data[surname.lower()] = hours_int
                        print(f"Найдены часы для {surname}: {hours_int}")
                except ValueError:
                    continue
    
    return hours_data

def test_messages():
    """Тестируем различные форматы сообщений"""
    test_cases = [
        "Ковшиков 50",
        "Иванов 8 Петров 10",
        "Сидоров: 6",
        "Кузнецов - 7",
        "Смирнов=9",
        "Попов 12 часов",
        "Волков 4, Орлов 5",
        "работал Федоров 8",
        "Морозов 25",  # Должно игнорироваться (больше 24)
        "Зайцев 0",    # Должно игнорироваться (меньше 1)
    ]
    
    for message in test_cases:
        print(f"\n--- Тестируем сообщение: '{message}' ---")
        result = extract_hours_from_message(message)
        print(f"Результат: {result}")

if __name__ == "__main__":
    test_messages()