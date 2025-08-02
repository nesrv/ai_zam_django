#!/usr/bin/env python
import os
import sys
import django
from datetime import date

# Настройка Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ai_zam.settings')
django.setup()

from sotrudniki.models import Sotrudnik, SotrudnikiZarplaty
from object.models import Objekt

def test_save_hours():
    print("Тестирование записи в таблицу sotrudniki_zarplaty...")
    
    # Получаем первого сотрудника и первый объект
    try:
        sotrudnik = Sotrudnik.objects.first()
        objekt = Objekt.objects.first()
        
        if not sotrudnik:
            print("Ошибка: Нет сотрудников в базе данных")
            return
            
        if not objekt:
            print("Ошибка: Нет объектов в базе данных")
            return
            
        print(f"Сотрудник: {sotrudnik.fio}")
        print(f"Объект: {objekt.nazvanie}")
        
        # Создаем запись в таблице зарплат
        zarplata, created = SotrudnikiZarplaty.objects.update_or_create(
            sotrudnik=sotrudnik,
            objekt=objekt,
            data=date.today(),
            defaults={
                'kolichestvo_chasov': 8.0,
                'kpi': 1.0,
                'vydano': False
            }
        )
        
        if created:
            print(f"[OK] Создана новая запись в sotrudniki_zarplaty с ID: {zarplata.id}")
        else:
            print(f"[OK] Обновлена существующая запись в sotrudniki_zarplaty с ID: {zarplata.id}")
            
        # Проверяем, что запись действительно сохранилась
        saved_record = SotrudnikiZarplaty.objects.get(id=zarplata.id)
        print(f"Проверка: {saved_record.sotrudnik.fio} - {saved_record.kolichestvo_chasov} часов")
        
        print("[OK] Тест успешно завершен!")
        
    except Exception as e:
        print(f"[ERROR] Ошибка: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_save_hours()