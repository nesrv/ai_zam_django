import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ai_zam.settings')
django.setup()

from object.models import (
    KadrovoeObespechenie, 
    MashinyMekhanizmy, 
    InstrumentMaterialy, 
    AdministrativnoBytovyeRashody, 
    SpecodezhaSiz
)

# Кадровое обеспечение
kadry_data = [
    ('ИТР', 'час'),
    ('Каменщик', 'час'),
    ('Подсобный рабочий', 'час'),
]

for naimenovanie, edinica in kadry_data:
    KadrovoeObespechenie.objects.get_or_create(
        naimenovanie=naimenovanie,
        edinica_izmereniya=edinica
    )

# Машины и механизмы
mashiny_data = [
    ('Минипогрузчик', 'час'),
    ('Автокран', 'час'),
]

for nazvanie, edinica in mashiny_data:
    MashinyMekhanizmy.objects.get_or_create(
        nazvanie=nazvanie,
        edinica_izmereniya=edinica
    )

# Инструмент и материалы
instrument_data = [
    ('Раствор', 'м3'),
    ('Кирпич полнотелый', 'шт'),
    ('Мелкие инструменты', 'шт'),
    ('ЗИП для страховочных систем', 'шт'),
    ('Транспорт/Доставка', 'шт'),
]

for nazvanie, edinica in instrument_data:
    InstrumentMaterialy.objects.get_or_create(
        nazvanie=nazvanie,
        edinica_izmereniya=edinica
    )

# Административно бытовые расходы
abr_data = [
    ('Канцелярские товары', 'шт'),
    ('Биотуалет', 'шт'),
]

for nazvanie, edinica in abr_data:
    AdministrativnoBytovyeRashody.objects.get_or_create(
        nazvanie=nazvanie,
        edinica_izmereniya=edinica
    )

# СИЗ спецодежда
siz_data = [
    ('Ботинки', 'пар'),
    ('Жилет сигнальный', 'шт'),
]

for nazvanie, edinica in siz_data:
    SpecodezhaSiz.objects.get_or_create(
        nazvanie=nazvanie,
        edinica_izmereniya=edinica
    )

print("Данные успешно добавлены!")