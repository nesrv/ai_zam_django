from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from .models import Objekt
from sotrudniki.models import Sotrudnik, Specialnost
from django.shortcuts import get_object_or_404

@csrf_exempt
def get_employees_simple(request, object_id):
    """Простой API-эндпоинт для получения сотрудников по объекту"""
    try:
        # Получаем объект
        obj = get_object_or_404(Objekt, id=object_id)
        
        # Получаем всех сотрудников, привязанных к объекту
        employees = obj.sotrudniki.all()
        
        # Если нет сотрудников на объекте, возвращаем всех сотрудников
        if employees.count() == 0:
            from sotrudniki.models import Sotrudnik
            employees = Sotrudnik.objects.all()[:5]  # Ограничиваем 5 сотрудниками для теста
        
        # Формируем список сотрудников с дополнительной информацией
        employees_data = []
        for employee in employees:
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