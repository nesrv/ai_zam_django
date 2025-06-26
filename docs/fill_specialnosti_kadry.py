import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ai_zam.settings')
django.setup()

from object.models import Specialnost, Kadry

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

# Создаем несколько тестовых кадров
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

print("Данные о специальностях и кадрах успешно добавлены!")