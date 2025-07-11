#!/usr/bin/env python
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ai_zam.settings')
django.setup()

from object.models import Objekt
from sotrudniki.models import Sotrudnik

# Получаем первый объект
obj = Objekt.objects.first()
print(f"Объект: {obj}")

# Получаем первого сотрудника
emp = Sotrudnik.objects.first()
print(f"Сотрудник: {emp}")

if obj and emp:
    # Добавляем сотрудника к объекту
    obj.sotrudniki.add(emp)
    print(f"Добавлен сотрудник {emp.fio} к объекту {obj.nazvanie}")
    
    # Проверяем связь
    employees = obj.sotrudniki.all()
    print(f"Сотрудники объекта: {list(employees)}")
    
    # Проверяем обратную связь
    objects = emp.objekty.all()
    print(f"Объекты сотрудника: {list(objects)}")
else:
    print("Нет данных для тестирования")