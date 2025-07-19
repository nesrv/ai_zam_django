from django.http import JsonResponse, HttpResponse
from django.views.decorators.csrf import csrf_exempt
from .models import Objekt
from sotrudniki.models import Sotrudnik, Specialnost
from django.shortcuts import get_object_or_404, render
import json

def employees_by_position_view(request, object_id):
    """Представление для страницы поиска сотрудников по должности"""
    obj = get_object_or_404(Objekt, id=object_id)
    return render(request, 'object/employees_by_position.html', {'object': obj})

@csrf_exempt
def debug_cell_info(request, object_id):
    """Отладочный эндпоинт для вывода информации о ячейке в терминал"""
    try:
        # Получаем параметры из запроса
        position = request.GET.get('position', '')
        date = request.GET.get('date', '')
        
        # Выводим информацию в терминал
        print(f"\n[DEBUG] Информация о ячейке:")
        print(f"ID объекта: {object_id}")
        print(f"Должность: {position}")
        print(f"Дата: {date}\n")
        
        # Возвращаем успешный ответ
        return JsonResponse({
            'success': True, 
            'message': 'Информация выведена в терминал',
            'debug_info': {
                'object_id': object_id,
                'position': position,
                'date': date
            }
        })
    except Exception as e:
        print(f"[ERROR] Ошибка в отладочном эндпоинте: {str(e)}")
        return JsonResponse({'success': False, 'error': str(e)})

@csrf_exempt
def get_employees_simple(request, object_id):
    """Простой API-эндпоинт для получения сотрудников по объекту и должности"""
    try:
        # Получаем должность из параметров запроса
        position = request.GET.get('position', '')
        
        # Получаем объект
        obj = get_object_or_404(Objekt, id=object_id)
        
        # Получаем всех сотрудников, привязанных к объекту
        employees = obj.sotrudniki.all()
        
        # Если нет сотрудников на объекте, возвращаем всех сотрудников
        if employees.count() == 0:
            from sotrudniki.models import Sotrudnik
            employees = Sotrudnik.objects.all()
        
        # Находим специальности, подходящие по названию
        specialnosti = Specialnost.objects.filter(nazvanie__icontains=position)
        
        # Если не нашли специальность, ищем по части слова
        if not specialnosti.exists() and position:
            words = position.split()
            for word in words:
                if len(word) > 3:  # Ищем только по словам длиннее 3 символов
                    specialnosti = specialnosti | Specialnost.objects.filter(nazvanie__icontains=word)
        
        # Фильтруем сотрудников по найденным специальностям
        filtered_employees = []
        if specialnosti.exists():
            for spec in specialnosti:
                filtered_employees.extend(employees.filter(specialnost=spec))
        else:
            # Если не нашли подходящих специальностей, возвращаем всех сотрудников
            filtered_employees = list(employees)
        
        # Удаляем дубликаты
        unique_employees = []
        employee_ids = set()
        for emp in filtered_employees:
            if emp.id not in employee_ids:
                employee_ids.add(emp.id)
                unique_employees.append(emp)
        
        # Формируем список сотрудников с дополнительной информацией
        employees_data = []
        for employee in unique_employees:
            employee_data = {
                'id': employee.id,
                'fio': employee.fio,
                'organizaciya': employee.organizaciya.nazvanie if employee.organizaciya else None,
                'podrazdelenie': employee.podrazdelenie.nazvanie if employee.podrazdelenie else None,
                'specialnost': employee.specialnost.nazvanie if employee.specialnost else None,
            }
            employees_data.append(employee_data)
        
        return JsonResponse({'success': True, 'employees': employees_data})
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)})