import os
import django
from datetime import date

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ai_zam.settings')
django.setup()

from object.models import Objekt, Resurs, ResursyPoObjektu, Kadry

# Создаем объект "Снежком"
objekt = Objekt.objects.create(
    nazvanie="Снежком",
    otvetstvennyj=Kadry.objects.first(),  # Берем первого доступного сотрудника
    data_nachala=date.today(),
    data_plan_zaversheniya=date(2025, 12, 31),
    status="планируется"
)

# Данные ресурсов для объекта "Снежком"
resursy_data = [
    # Кадровое обеспечение
    ("ИТР", 600, 500.00, "план"),
    ("Каменщик", 700, 450.00, "план"),
    ("Подсобный рабочий", 1200, 400.00, "план"),
    
    # Машины и механизмы
    ("Минипогрузчик", 120, 2500.00, "план"),
    ("Автокран", 80, 3750.00, "план"),
    
    # Инструмент и материалы
    ("Раствор", 100, 700.00, "план"),
    ("Кирпич полнотелый", 215040, 25.00, "план"),
    ("Мелкие инструменты", 1, 5000.00, "план"),
    ("ЗИП для страховочных систем", 10, 9000.00, "план"),
    ("Транспорт/Доставка", 10, 3000.00, "план"),
    
    # Административно бытовые расходы
    ("Канцелярские товары", 3, 1200.00, "план"),
    ("Биотуалет", 3, 10000.00, "план"),
    
    # СИЗ спецодежда
    ("Ботинки", 10, 4500.00, "план"),
    ("Жилет сигнальный", 10, 700.00, "план"),
    
    # Подрядные организации
    ("Устройство временного ограждения", 300, 5250.00, "план"),
    ("Устройство временного освещения", 1, 60000.00, "план"),
]

# Добавляем ресурсы к объекту
for naimenovanie, kolichestvo, cena, tip in resursy_data:
    try:
        resurs = Resurs.objects.get(naimenovanie=naimenovanie)
        ResursyPoObjektu.objects.create(
            objekt=objekt,
            resurs=resurs,
            kolichestvo=kolichestvo,
            cena=cena,
            tip=tip
        )
        print(f"Добавлен ресурс: {naimenovanie}")
    except Resurs.DoesNotExist:
        print(f"Ресурс не найден: {naimenovanie}")

print(f"Объект '{objekt.nazvanie}' успешно создан с ресурсами!")