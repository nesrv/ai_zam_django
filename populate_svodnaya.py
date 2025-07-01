import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ai_zam.settings')
django.setup()

from object.models import Objekt, RaskhodResursa, DokhodResursa, SvodnayaRaskhodDokhodPoDnyam
from django.db.models import Sum

# Очищаем таблицу
SvodnayaRaskhodDokhodPoDnyam.objects.all().delete()

# Получаем все уникальные комбинации объект-дата
dates_objects = set()

for raskhod in RaskhodResursa.objects.all():
    objekt = raskhod.fakticheskij_resurs.resurs_po_objektu.objekt
    dates_objects.add((objekt.id, raskhod.data))
    
for dokhod in DokhodResursa.objects.all():
    objekt = dokhod.fakticheskij_resurs.resurs_po_objektu.objekt
    dates_objects.add((objekt.id, dokhod.data))

# Создаем записи в сводной таблице
for objekt_id, data in dates_objects:
    objekt = Objekt.objects.get(id=objekt_id)
    
    # Расходы: Σ (Расценка × Дневной расход) для всех категорий кроме подрядных организаций
    raskhod_total = 0
    raskhody = RaskhodResursa.objects.filter(
        fakticheskij_resurs__resurs_po_objektu__objekt=objekt,
        data=data
    ).exclude(
        fakticheskij_resurs__resurs_po_objektu__resurs__kategoriya_resursa__nazvanie='Подрядные организации'
    )
    
    for rashod in raskhody:
        cena = float(rashod.fakticheskij_resurs.resurs_po_objektu.cena)
        raskhod_total += cena * float(rashod.izraskhodovano)
    
    # Доходы: Σ (Расценка × Дневной доход) для подрядных организаций
    dokhod_total = 0
    dokhody = DokhodResursa.objects.filter(
        fakticheskij_resurs__resurs_po_objektu__objekt=objekt,
        data=data,
        fakticheskij_resurs__resurs_po_objektu__resurs__kategoriya_resursa__nazvanie='Подрядные организации'
    )
    
    for dokhod in dokhody:
        cena = float(dokhod.fakticheskij_resurs.resurs_po_objektu.cena)
        dokhod_total += cena * float(dokhod.vypolneno)
    
    SvodnayaRaskhodDokhodPoDnyam.objects.create(
        objekt=objekt,
        data=data,
        raskhod=raskhod_total,
        dokhod=dokhod_total,
        balans=dokhod_total - raskhod_total
    )

print(f'Создано {len(dates_objects)} записей в сводной таблице')