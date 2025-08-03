import os
import django
from datetime import date, datetime, timedelta
import random

# Настройка Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ai_zam.settings')
django.setup()

from object.models import Objekt, ResursyPoObjektu, FakticheskijResursPoObjektu, RaskhodResursa, DokhodResursa, Resurs, KategoriyaResursa

def fill_income_demo_data():
    try:
        demo_obj = Objekt.objects.get(id=42)
        
        # Получаем доходные ресурсы (raskhod_dokhod=False)
        income_resources = ResursyPoObjektu.objects.filter(
            objekt=demo_obj,
            resurs__kategoriya_resursa__raskhod_dokhod=False
        )
        
        print(f"Найдено доходных ресурсов: {income_resources.count()}")
        
        # Создаем доходы за последние 30 дней
        total_income_records = 0
        
        for resurs_po_obj in income_resources:
            # Получаем или создаем фактический ресурс
            fakt_resurs, created = FakticheskijResursPoObjektu.objects.get_or_create(
                resurs_po_objektu=resurs_po_obj
            )
            
            # Создаем доходы за последние 30 дней
            for i in range(30):
                current_date = date.today() - timedelta(days=i)
                
                # Случайно создаем доходы (40% вероятность)
                if random.choice([True, False, False, True, False]):
                    # Доход от 1% до 15% от общего количества
                    max_dokhod = float(resurs_po_obj.kolichestvo) * 0.15
                    dokhod = round(random.uniform(0.5, max_dokhod), 2)
                    
                    # Создаем запись дохода
                    dokhod_record, created = DokhodResursa.objects.get_or_create(
                        fakticheskij_resurs=fakt_resurs,
                        data=current_date,
                        defaults={'vypolneno': dokhod}
                    )
                    
                    if created:
                        total_income_records += 1
                    
                    # Также создаем соответствующую запись в RaskhodResursa для отображения
                    RaskhodResursa.objects.get_or_create(
                        fakticheskij_resurs=fakt_resurs,
                        data=current_date,
                        defaults={'izraskhodovano': dokhod}
                    )
        
        print(f"Демо-данные доходов созданы для объекта ID 42:")
        print(f"- Записей доходов: {total_income_records}")
        print(f"- Доходных ресурсов: {income_resources.count()}")
        
        # Проверяем общее количество записей доходов
        total_dokhod_records = DokhodResursa.objects.filter(
            fakticheskij_resurs__resurs_po_objektu__objekt=demo_obj
        ).count()
        print(f"- Всего записей доходов в базе: {total_dokhod_records}")
        
    except Objekt.DoesNotExist:
        print("Объект с ID 42 не найден")

if __name__ == '__main__':
    fill_income_demo_data()