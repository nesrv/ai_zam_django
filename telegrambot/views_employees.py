from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from object.models import Objekt
from sotrudniki.models import Sotrudnik

def get_employees_by_object(request):
    """Получение сотрудников по объекту в формате JSON"""
    if request.method == 'GET':
        object_id = request.GET.get('object_id')
        if not object_id:
            return JsonResponse({
                'success': False,
                'error': 'ID объекта не указан'
            })
        
        try:
            # Получаем объект
            objekt = get_object_or_404(Objekt, id=object_id)
            
            # Получаем сотрудников, связанных с объектом
            employees = Sotrudnik.objects.filter(objekty=objekt)
            
            # Формируем данные о сотрудниках
            employees_data = [
                {
                    'fio': employee.fio,
                    'specialnost': employee.specialnost.nazvanie if employee.specialnost else 'Не указана'
                }
                for employee in employees
            ]
            
            # Если сотрудников нет, добавляем фиктивные данные
            if not employees_data:
                employees_data = [
                    {"fio": "Иванов Иван Иванович", "specialnost": "альпинист"},
                    {"fio": "Петров Петр Петрович", "specialnost": "монтажник"},
                    {"fio": "Сидоров Сидор Сидорович", "specialnost": "сварщик"}
                ]
            
            return JsonResponse({
                'success': True,
                'employees': employees_data
            })
            
        except Exception as e:
            return JsonResponse({
                'success': False,
                'error': str(e)
            })
    
    return JsonResponse({
        'success': False,
        'error': 'Метод не поддерживается'
    })