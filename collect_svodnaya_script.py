#!/usr/bin/env python
import os
import sys
import django
from datetime import datetime, timedelta

# Настройка Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ai_zam.settings')
django.setup()

from django.db.models import Sum, F
from object.models import (
    RaskhodResursa, DokhodResursa, SvodnayaRaskhodDokhodPoDnyam, 
    Objekt, ResursyPoObjektu, FakticheskijResursPoObjektu
)

def collect_svodnaya_data():
    """Собирает данные из итоговых строк расходов и доходов по дням в svodnaya_raskhod_dokhod_po_dnyam"""
    
    print("Начинаем сбор данных из итоговых строк...")
    
    # Очищаем сводную таблицу
    deleted_count = SvodnayaRaskhodDokhodPoDnyam.objects.all().delete()[0]
    print(f"Удалено {deleted_count} старых записей")
    
    # Получаем все объекты
    objekty = Objekt.objects.all()
    
    # Создаем 20 дней для анализа
    today = datetime.now().date()
    days = [today - timedelta(days=i) for i in range(20)]
    
    created_count = 0
    
    for objekt in objekty:
        print(f"Обрабатываем объект: {objekt.nazvanie}")
        
        for day in days:
            # Вычисляем итоговые фактические расходы по дням
            # (из строки "Итого фактических расходов по дням")
            total_raskhod = 0.0
            
            # Получаем все ресурсы объекта (кроме подрядных организаций)
            resources = ResursyPoObjektu.objects.filter(
                objekt=objekt
            ).exclude(
                resurs__kategoriya_resursa__nazvanie='Подрядные организации'
            ).select_related('resurs', 'resurs__kategoriya_resursa')
            
            for resource in resources:
                # Ищем фактические ресурсы
                try:
                    fr = FakticheskijResursPoObjektu.objects.get(resurs_po_objektu=resource)
                    # Ищем расходы за этот день
                    rashody = RaskhodResursa.objects.filter(
                        fakticheskij_resurs=fr,
                        data=day
                    )
                    for rashod in rashody:
                        # Расход = Заплан.цена × Дневной расход
                        expense_amount = float(resource.cena) * float(rashod.izraskhodovano)
                        total_raskhod += expense_amount
                except FakticheskijResursPoObjektu.DoesNotExist:
                    continue
            
            # Вычисляем итоговые фактические доходы по дням
            # (из строки "Итого фактических доходов по дням")
            total_dokhod = 0.0
            
            # Получаем ресурсы подрядных организаций
            income_resources = ResursyPoObjektu.objects.filter(
                objekt=objekt,
                resurs__kategoriya_resursa__nazvanie='Подрядные организации'
            ).select_related('resurs', 'resurs__kategoriya_resursa')
            
            for resource in income_resources:
                # Ищем фактические ресурсы
                try:
                    fr = FakticheskijResursPoObjektu.objects.get(resurs_po_objektu=resource)
                    # Ищем доходы за этот день
                    dokhody = DokhodResursa.objects.filter(
                        fakticheskij_resurs=fr,
                        data=day
                    )
                    for dokhod in dokhody:
                        # Доход = Расценка × Дневной доход
                        income_amount = float(resource.cena) * float(dokhod.vypolneno)
                        total_dokhod += income_amount
                except FakticheskijResursPoObjektu.DoesNotExist:
                    continue
            
            # Создаем запись только если есть расходы или доходы
            if total_raskhod > 0 or total_dokhod > 0:
                balans = total_dokhod - total_raskhod
                
                SvodnayaRaskhodDokhodPoDnyam.objects.create(
                    objekt=objekt,
                    data=day,
                    raskhod=total_raskhod,
                    dokhod=total_dokhod,
                    balans=balans
                )
                created_count += 1
                print(f"  {day}: расход={total_raskhod:.2f}, доход={total_dokhod:.2f}, баланс={balans:.2f}")
    
    print(f"Создано {created_count} записей в сводной таблице")
    print("Сбор данных завершен!")

if __name__ == "__main__":
    collect_svodnaya_data()