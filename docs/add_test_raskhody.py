import os
import django
from datetime import date, timedelta

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ai_zam.settings')
django.setup()

from object.models import Objekt, ResursyPoObjektu, FakticheskijResursPoObjektu, RaskhodResursa

# Получаем объект с ID=2
try:
    objekt = Objekt.objects.get(id=2)
    print(f"Найден объект: {objekt.nazvanie}")
    
    # Получаем ресурсы этого объекта
    resursy = ResursyPoObjektu.objects.filter(objekt=objekt)[:3]  # Берем первые 3 ресурса
    
    for resurs_po_objektu in resursy:
        # Создаем фактический ресурс
        fakt_resurs, created = FakticheskijResursPoObjektu.objects.get_or_create(
            resurs_po_objektu=resurs_po_objektu
        )
        
        if created:
            print(f"Создан фактический ресурс для: {resurs_po_objektu.resurs.naimenovanie}")
        
        # Добавляем несколько записей расходов за последние дни
        for i in range(5):
            data_raskhoda = date.today() - timedelta(days=i)
            RaskhodResursa.objects.get_or_create(
                fakticheskij_resurs=fakt_resurs,
                data=data_raskhoda,
                defaults={'izraskhodovano': 10 + i * 5}
            )
            print(f"Добавлен расход на {data_raskhoda}: {10 + i * 5}")
    
    print("Тестовые данные добавлены!")
    
except Objekt.DoesNotExist:
    print("Объект с ID=2 не найден")