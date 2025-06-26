import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ai_zam.settings')
django.setup()

from object.models import KategoriyaResursa, Resurs, Specialnost, Kadry
from datetime import date

# Создаем категории ресурсов
kategorii = [
    "Кадровое обеспечение",
    "Машины и механизмы", 
    "Инструмент и материалы",
    "Административно бытовые расходы",
    "СИЗ спецодежда",
    "Подрядные организации"
]

for kat in kategorii:
    KategoriyaResursa.objects.get_or_create(nazvanie=kat)

# Создаем ресурсы
resursy_data = [
    # Кадровое обеспечение
    ("ИТР", "час", "Кадровое обеспечение"),
    ("Каменщик", "час", "Кадровое обеспечение"),
    ("Подсобный рабочий", "час", "Кадровое обеспечение"),
    
    # Машины и механизмы
    ("Минипогрузчик", "час", "Машины и механизмы"),
    ("Автокран", "час", "Машины и механизмы"),
    
    # Инструмент и материалы
    ("Раствор", "м3", "Инструмент и материалы"),
    ("Кирпич полнотелый", "шт", "Инструмент и материалы"),
    ("Мелкие инструменты", "шт", "Инструмент и материалы"),
    ("ЗИП для страховочных систем", "шт", "Инструмент и материалы"),
    ("Транспорт/Доставка", "шт", "Инструмент и материалы"),
    
    # Административно бытовые расходы
    ("Канцелярские товары", "шт", "Административно бытовые расходы"),
    ("Биотуалет", "шт", "Административно бытовые расходы"),
    
    # СИЗ спецодежда
    ("Ботинки", "пар", "СИЗ спецодежда"),
    ("Жилет сигнальный", "шт", "СИЗ спецодежда"),
    
    # Подрядные организации
    ("Устройство временного ограждения", "м", "Подрядные организации"),
    ("Устройство временного освещения", "шт", "Подрядные организации"),
]

for naimenovanie, edinica, kategoriya_name in resursy_data:
    kategoriya = KategoriyaResursa.objects.get(nazvanie=kategoriya_name)
    Resurs.objects.get_or_create(
        naimenovanie=naimenovanie,
        edinica_izmereniya=edinica,
        kategoriya_resursa=kategoriya
    )

# Создаем специальности
specialnosti = [
    "Инженер",
    "Каменщик", 
    "Сварщик",
    "Электрик",
    "Плотник",
    "Монтажник",
]

for spec in specialnosti:
    Specialnost.objects.get_or_create(nazvanie=spec)

# Создаем кадры
kadry_data = [
    {
        "fio": "Иванов Иван Иванович",
        "specialnost": "Инженер",
        "razryad": "1",
        "pasport": "1234 567890",
        "telefon": "+7 (999) 123-45-67"
    },
    {
        "fio": "Петров Петр Петрович", 
        "specialnost": "Каменщик",
        "razryad": "3",
        "pasport": "2345 678901",
        "telefon": "+7 (999) 234-56-78"
    },
    {
        "fio": "Сидоров Сидор Сидорович",
        "specialnost": "Сварщик",
        "razryad": "4", 
        "pasport": "3456 789012",
        "telefon": "+7 (999) 345-67-89"
    }
]

for kadr in kadry_data:
    spec = Specialnost.objects.get(nazvanie=kadr["specialnost"])
    Kadry.objects.get_or_create(
        fio=kadr["fio"],
        specialnost=spec,
        razryad=kadr["razryad"],
        pasport=kadr["pasport"],
        telefon=kadr["telefon"]
    )

print("Данные успешно добавлены!")