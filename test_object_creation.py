#!/usr/bin/env python
"""
Скрипт для тестирования создания объекта из JSON файла
"""

import os
import sys
import django

# Настройка Django
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ai_zam.settings')
django.setup()

from object.models import Objekt, KategoriyaResursa, Resurs, ResursyPoObjektu
from sotrudniki.models import Specialnost, Podrazdelenie

def test_object_creation():
    """Тестирование создания объекта"""
    print("Тестирование создания объекта из JSON...")
    
    # Проверяем количество объектов до создания
    objects_before = Objekt.objects.count()
    categories_before = KategoriyaResursa.objects.count()
    resources_before = Resurs.objects.count()
    specialties_before = Specialnost.objects.count()
    
    print(f"До создания:")
    print(f"   Объектов: {objects_before}")
    print(f"   Категорий: {categories_before}")
    print(f"   Ресурсов: {resources_before}")
    print(f"   Специальностей: {specialties_before}")
    
    # Имитируем запрос к view
    from telegrambot.views import create_object_from_json
    from django.http import HttpRequest
    import json
    
    request = HttpRequest()
    request.method = 'POST'
    request._body = json.dumps({}).encode('utf-8')
    
    try:
        response = create_object_from_json(request)
        response_data = json.loads(response.content.decode('utf-8'))
        
        if response_data.get('ok'):
            print(f"Объект успешно создан!")
            print(f"   ID: {response_data['object_id']}")
            print(f"   Название: {response_data['object_name']}")
            print(f"   JSON файл: {response_data['json_file']}")
            
            # Проверяем количество после создания
            objects_after = Objekt.objects.count()
            categories_after = KategoriyaResursa.objects.count()
            resources_after = Resurs.objects.count()
            specialties_after = Specialnost.objects.count()
            
            print(f"После создания:")
            print(f"   Объектов: {objects_after} (+{objects_after - objects_before})")
            print(f"   Категорий: {categories_after} (+{categories_after - categories_before})")
            print(f"   Ресурсов: {resources_after} (+{resources_after - resources_before})")
            print(f"   Специальностей: {specialties_after} (+{specialties_after - specialties_before})")
            
            # Показываем детали созданного объекта
            obj = Objekt.objects.get(id=response_data['object_id'])
            print(f"\nДетали объекта '{obj.nazvanie}':")
            
            # Ресурсы по объекту
            resources_by_obj = ResursyPoObjektu.objects.filter(objekt=obj)
            print(f"   Ресурсов по объекту: {resources_by_obj.count()}")
            
            # Группируем по категориям
            categories = {}
            for res_obj in resources_by_obj:
                cat_name = res_obj.resurs.kategoriya_resursa.nazvanie
                if cat_name not in categories:
                    categories[cat_name] = []
                categories[cat_name].append({
                    'name': res_obj.resurs.naimenovanie,
                    'quantity': res_obj.kolichestvo,
                    'price': res_obj.cena,
                    'unit': res_obj.resurs.edinica_izmereniya
                })
            
            for cat_name, items in categories.items():
                print(f"   {cat_name}: {len(items)} ресурсов")
                for item in items[:3]:  # Показываем первые 3
                    print(f"      - {item['name']}: {item['quantity']} {item['unit']} по {item['price']} руб.")
                if len(items) > 3:
                    print(f"      ... и еще {len(items) - 3} ресурсов")
            
        else:
            print(f"Ошибка создания объекта: {response_data.get('error')}")
            
    except Exception as e:
        print(f"Исключение при тестировании: {e}")
        import traceback
        traceback.print_exc()

if __name__ == '__main__':
    test_object_creation()