from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from .models import Objekt
from sotrudniki.models import Sotrudnik, Specialnost

def get_employees_by_position(request, object_id):
    """API для получения сотрудников по должности"""
    position = request.GET.get('position', '')
    
    # Получаем объект
    obj = get_object_or_404(Objekt, id=object_id)
    
    # Находим специальности, подходящие по названию
    specialnosti = Specialnost.objects.filter(nazvanie__icontains=position)
    
    # Если не нашли специальность, ищем по части слова
    if not specialnosti.exists() and position:
        words = position.split()
        for word in words:
            if len(word) > 3:  # Ищем только по словам длиннее 3 символов
                specialnosti = specialnosti | Specialnost.objects.filter(nazvanie__icontains=word)
    
    # Получаем всех сотрудников
    employees = Sotrudnik.objects.all()
    
    # Фильтруем по специальностям, если они найдены
    if specialnosti.exists():
        filtered_employees = []
        for spec in specialnosti:
            filtered_employees.extend(employees.filter(specialnost=spec))
        employees = filtered_employees
    
    # Ограничиваем количество сотрудников
    if not employees:
        employees = Sotrudnik.objects.all()[:5]
    
    # Формируем список сотрудников
    employees_data = []
    for employee in employees:
        employees_data.append({
            'id': employee.id,
            'fio': employee.fio,
            'organizaciya': employee.organizaciya.nazvanie if employee.organizaciya else None,
            'podrazdelenie': employee.podrazdelenie.nazvanie if employee.podrazdelenie else None,
            'specialnost': employee.specialnost.nazvanie if employee.specialnost else None,
        })
    
    return JsonResponse({'success': True, 'employees': employees_data})