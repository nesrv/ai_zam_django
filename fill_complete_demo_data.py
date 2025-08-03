import os
import django
from datetime import date, datetime, timedelta
import random

# Настройка Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ai_zam.settings')
django.setup()

from object.models import Objekt, ResursyPoObjektu, FakticheskijResursPoObjektu, RaskhodResursa, Resurs, KategoriyaResursa
from sotrudniki.models import Organizaciya, Sotrudnik, Specialnost, Podrazdelenie, SotrudnikiZarplaty, OrganizaciyaPodrazdelenie

def fill_complete_demo_data():
    try:
        demo_obj = Objekt.objects.get(id=42)
        
        # Создаем дополнительные категории ресурсов
        categories_data = [
            {'name': 'Материалы', 'raskhod_dokhod': True, 'order': 2},
            {'name': 'Техника', 'raskhod_dokhod': True, 'order': 3},
            {'name': 'Инструменты', 'raskhod_dokhod': True, 'order': 4},
            {'name': 'Подрядные организации', 'raskhod_dokhod': False, 'order': 5},
        ]
        
        for cat_data in categories_data:
            KategoriyaResursa.objects.get_or_create(
                nazvanie=cat_data['name'],
                defaults={
                    'raskhod_dokhod': cat_data['raskhod_dokhod'],
                    'order': cat_data['order']
                }
            )
        
        # Создаем ресурсы для каждой категории
        resources_data = [
            # Материалы
            {'name': 'Цемент М400', 'unit': 'т', 'category': 'Материалы', 'quantity': 50, 'price': 8500},
            {'name': 'Арматура А500С', 'unit': 'т', 'category': 'Материалы', 'quantity': 20, 'price': 45000},
            {'name': 'Кирпич керамический', 'unit': 'тыс.шт', 'category': 'Материалы', 'quantity': 100, 'price': 12000},
            {'name': 'Песок строительный', 'unit': 'м³', 'category': 'Материалы', 'quantity': 200, 'price': 1200},
            
            # Техника
            {'name': 'Экскаватор JCB', 'unit': 'смена', 'category': 'Техника', 'quantity': 30, 'price': 15000},
            {'name': 'Автокран 25т', 'unit': 'смена', 'category': 'Техника', 'quantity': 20, 'price': 18000},
            {'name': 'Бетономешалка', 'unit': 'смена', 'category': 'Техника', 'quantity': 40, 'price': 3500},
            
            # Инструменты
            {'name': 'Перфоратор Bosch', 'unit': 'шт', 'category': 'Инструменты', 'quantity': 10, 'price': 25000},
            {'name': 'Болгарка 230мм', 'unit': 'шт', 'category': 'Инструменты', 'quantity': 15, 'price': 8000},
            {'name': 'Сварочный аппарат', 'unit': 'шт', 'category': 'Инструменты', 'quantity': 5, 'price': 35000},
            
            # Подрядные организации
            {'name': 'Электромонтажные работы', 'unit': 'м²', 'category': 'Подрядные организации', 'quantity': 500, 'price': 2500},
            {'name': 'Сантехнические работы', 'unit': 'точка', 'category': 'Подрядные организации', 'quantity': 50, 'price': 8000},
            {'name': 'Отделочные работы', 'unit': 'м²', 'category': 'Подрядные организации', 'quantity': 800, 'price': 1800},
        ]
        
        for res_data in resources_data:
            category = KategoriyaResursa.objects.get(nazvanie=res_data['category'])
            
            resurs, created = Resurs.objects.get_or_create(
                naimenovanie=res_data['name'],
                defaults={
                    'edinica_izmereniya': res_data['unit'],
                    'kategoriya_resursa': category
                }
            )
            
            # Создаем ресурс по объекту
            resurs_po_obj, created = ResursyPoObjektu.objects.get_or_create(
                objekt=demo_obj,
                resurs=resurs,
                defaults={
                    'kolichestvo': res_data['quantity'],
                    'cena': res_data['price']
                }
            )
            
            # Создаем фактический ресурс
            fakt_resurs, created = FakticheskijResursPoObjektu.objects.get_or_create(
                resurs_po_objektu=resurs_po_obj
            )
            
            # Создаем расходы за последние 30 дней
            for i in range(30):
                current_date = date.today() - timedelta(days=i)
                
                # Случайно создаем расходы (не каждый день)
                if random.choice([True, False, False]):  # 33% вероятность
                    # Расход от 1% до 10% от общего количества
                    max_rashod = res_data['quantity'] * 0.1
                    rashod = round(random.uniform(0.1, max_rashod), 2)
                    
                    RaskhodResursa.objects.get_or_create(
                        fakticheskij_resurs=fakt_resurs,
                        data=current_date,
                        defaults={'izraskhodovano': rashod}
                    )
            
            # Обновляем потрачено
            total_spent = RaskhodResursa.objects.filter(fakticheskij_resurs=fakt_resurs).aggregate(
                total=django.db.models.Sum('izraskhodovano')
            )['total'] or 0
            
            resurs_po_obj.potracheno = total_spent
            resurs_po_obj.save()
        
        print(f"Полные демо-данные созданы для объекта ID 42:")
        print(f"- Категорий ресурсов: {KategoriyaResursa.objects.count()}")
        print(f"- Ресурсов: {Resurs.objects.count()}")
        print(f"- Ресурсов по объекту: {ResursyPoObjektu.objects.filter(objekt=demo_obj).count()}")
        print(f"- Расходов ресурсов: {RaskhodResursa.objects.filter(fakticheskij_resurs__resurs_po_objektu__objekt=demo_obj).count()}")
        
    except Objekt.DoesNotExist:
        print("Объект с ID 42 не найден")

if __name__ == '__main__':
    fill_complete_demo_data()