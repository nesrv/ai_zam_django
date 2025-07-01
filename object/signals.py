from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from django.db.models import Sum
from .models import RaskhodResursa, DokhodResursa, SvodnayaRaskhodDokhodPoDnyam

def update_svodnaya(objekt, data):
    """Обновляет сводную таблицу для конкретного объекта и даты"""
    # Расходы: Σ (Расценка × Дневной расход) для всех категорий кроме подрядных
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
    
    # Обновляем или создаем запись
    svodnaya, created = SvodnayaRaskhodDokhodPoDnyam.objects.update_or_create(
        objekt=objekt,
        data=data,
        defaults={
            'raskhod': raskhod_total,
            'dokhod': dokhod_total,
            'balans': dokhod_total - raskhod_total
        }
    )

@receiver(post_save, sender=RaskhodResursa)
def update_svodnaya_on_raskhod_save(sender, instance, **kwargs):
    objekt = instance.fakticheskij_resurs.resurs_po_objektu.objekt
    update_svodnaya(objekt, instance.data)

@receiver(post_delete, sender=RaskhodResursa)
def update_svodnaya_on_raskhod_delete(sender, instance, **kwargs):
    objekt = instance.fakticheskij_resurs.resurs_po_objektu.objekt
    update_svodnaya(objekt, instance.data)

@receiver(post_save, sender=DokhodResursa)
def update_svodnaya_on_dokhod_save(sender, instance, **kwargs):
    objekt = instance.fakticheskij_resurs.resurs_po_objektu.objekt
    update_svodnaya(objekt, instance.data)

@receiver(post_delete, sender=DokhodResursa)
def update_svodnaya_on_dokhod_delete(sender, instance, **kwargs):
    objekt = instance.fakticheskij_resurs.resurs_po_objektu.objekt
    update_svodnaya(objekt, instance.data)