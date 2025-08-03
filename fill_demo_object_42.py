import os
import django
from datetime import date, datetime, timedelta
import random

# Настройка Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ai_zam.settings')
django.setup()

from object.models import Objekt, ResursyPoObjektu, FakticheskijResursPoObjektu, RaskhodResursa, Resurs, KategoriyaResursa
from sotrudniki.models import Organizaciya, Sotrudnik, Specialnost, Podrazdelenie, SotrudnikiZarplaty, OrganizaciyaPodrazdelenie

def fill_object_42_demo_data():
    try:
        # Получаем объект с ID 42
        demo_obj = Objekt.objects.get(id=42)
        demo_obj.demo = True
        demo_obj.save()
        
        # Создаем демо-организацию если её нет
        demo_org, created = Organizaciya.objects.get_or_create(
            nazvanie="ООО ДЕМО-СТРОЙ",
            defaults={
                'inn': '1234567890',
                'ogrn': '1234567890123',
                'adres': 'г. Москва, ул. Демонстрационная, д. 1',
                'is_active': True
            }
        )
        
        # Связываем объект с организацией
        demo_obj.organizacii.add(demo_org)
        
        # Добавляем подразделение
        podrazdelenie = Podrazdelenie.objects.get(id=3)
        OrganizaciyaPodrazdelenie.objects.get_or_create(
            organizaciya=demo_org,
            podrazdelenie=podrazdelenie
        )
        
        # Создаем специальности
        specialnosti = ['Альпинист', 'Газорезчик', 'Сварщик', 'Монтажник', 'Стропальщик', 'Бетонщик', 'Арматурщик', 'Плотник', 'Электрик', 'Подсобный рабочий']
        
        for spec_name in specialnosti:
            Specialnost.objects.get_or_create(nazvanie=spec_name)
        
        # Создаем демо-сотрудников
        demo_employees = [
            {'fio': 'Иванов Иван Иванович', 'specialnost': 'Альпинист'},
            {'fio': 'Петров Петр Петрович', 'specialnost': 'Газорезчик'},
            {'fio': 'Сидоров Сидор Сидорович', 'specialnost': 'Сварщик'},
            {'fio': 'Козлов Андрей Викторович', 'specialnost': 'Монтажник'},
            {'fio': 'Морозов Дмитрий Александрович', 'specialnost': 'Стропальщик'},
            {'fio': 'Волков Сергей Николаевич', 'specialnost': 'Бетонщик'},
            {'fio': 'Лебедев Алексей Игоревич', 'specialnost': 'Арматурщик'},
            {'fio': 'Новиков Владимир Олегович', 'specialnost': 'Плотник'},
            {'fio': 'Федоров Михаил Васильевич', 'specialnost': 'Электрик'},
            {'fio': 'Михайлов Роман Сергеевич', 'specialnost': 'Подсобный рабочий'}
        ]
        
        created_employees = []
        for emp_data in demo_employees:
            specialnost = Specialnost.objects.get(nazvanie=emp_data['specialnost'])
            emp, created = Sotrudnik.objects.get_or_create(
                fio=emp_data['fio'],
                defaults={
                    'organizaciya': demo_org,
                    'specialnost': specialnost,
                    'podrazdelenie': podrazdelenie,
                    'data_rozhdeniya': date(1985, 1, 1),
                    'data_priema': date.today() - timedelta(days=90),
                    'data_nachala_raboty': date.today() - timedelta(days=90),
                    'pol': 'мужской'
                }
            )
            created_employees.append(emp)
            demo_obj.sotrudniki.add(emp)
        
        # Создаем категории ресурсов
        kadrovoe_cat, created = KategoriyaResursa.objects.get_or_create(
            nazvanie="Кадровое обеспечение",
            defaults={'raskhod_dokhod': True, 'order': 1}
        )
        
        # Создаем ресурсы для каждой специальности
        for spec_name in specialnosti:
            resurs, created = Resurs.objects.get_or_create(
                naimenovanie=spec_name,
                defaults={
                    'edinica_izmereniya': 'час',
                    'kategoriya_resursa': kadrovoe_cat
                }
            )
            
            # Создаем ресурс по объекту
            resurs_po_obj, created = ResursyPoObjektu.objects.get_or_create(
                objekt=demo_obj,
                resurs=resurs,
                defaults={
                    'kolichestvo': 160,
                    'cena': random.randint(800, 1500)
                }
            )
            
            # Создаем фактический ресурс
            fakt_resurs, created = FakticheskijResursPoObjektu.objects.get_or_create(
                resurs_po_objektu=resurs_po_obj
            )
        
        # Создаем записи зарплат за последние 30 дней
        for i in range(30):
            current_date = date.today() - timedelta(days=i)
            
            for emp in created_employees:
                if random.choice([True, False, True]):
                    hours = random.randint(6, 10)
                    kpi = round(random.uniform(0.8, 1.2), 2)
                    
                    SotrudnikiZarplaty.objects.get_or_create(
                        sotrudnik=emp,
                        objekt=demo_obj,
                        data=current_date,
                        defaults={
                            'kolichestvo_chasov': hours,
                            'kpi': kpi,
                            'vydano': random.choice([True, False])
                        }
                    )
                    
                    # Создаем расход ресурса
                    if emp.specialnost:
                        try:
                            resurs = Resurs.objects.get(naimenovanie=emp.specialnost.nazvanie)
                            resurs_po_obj = ResursyPoObjektu.objects.get(objekt=demo_obj, resurs=resurs)
                            fakt_resurs = FakticheskijResursPoObjektu.objects.get(resurs_po_objektu=resurs_po_obj)
                            
                            RaskhodResursa.objects.get_or_create(
                                fakticheskij_resurs=fakt_resurs,
                                data=current_date,
                                defaults={'izraskhodovano': hours}
                            )
                        except:
                            pass
        
        print(f"Демо-данные для объекта ID 42 созданы:")
        print(f"- Объект: {demo_obj.nazvanie}")
        print(f"- Организация: {demo_org.nazvanie}")
        print(f"- Сотрудников: {len(created_employees)}")
        print(f"- Записей зарплат: {SotrudnikiZarplaty.objects.filter(objekt=demo_obj).count()}")
        
    except Objekt.DoesNotExist:
        print("Объект с ID 42 не найден")

if __name__ == '__main__':
    fill_object_42_demo_data()