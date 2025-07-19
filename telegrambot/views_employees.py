from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from object.models import Objekt
from sotrudniki.models import Sotrudnik
import json
import logging

logger = logging.getLogger(__name__)

@csrf_exempt
def get_employees_by_object(request):
    """Получение списка сотрудников по объекту для модального окна"""
    try:
        object_id = request.GET.get('object_id')
        
        if not object_id:
            return JsonResponse({
                'success': False,
                'error': 'Не указан ID объекта'
            })
        
        # Получаем объект
        try:
            objekt = Objekt.objects.get(id=object_id)
        except Objekt.DoesNotExist:
            return JsonResponse({
                'success': False,
                'error': f'Объект с ID {object_id} не найден'
            })
        
        # Получаем сотрудников, связанных с объектом
        employees = objekt.sotrudniki.filter(is_active=True)
        
        # Если сотрудников нет, возвращаем пустой список
        if not employees:
            return JsonResponse({
                'success': True,
                'employees': []
            })
        
        # Формируем список сотрудников с их специальностями
        employees_data = []
        for employee in employees:
            specialnost = employee.specialnost.nazvanie if employee.specialnost else "Не указана"
            # Добавляем фамилию отдельно для поиска
            surname = employee.fio.split(' ')[0] if employee.fio else ""
            employees_data.append({
                "fio": employee.fio,
                "specialnost": specialnost,
                "surname": surname,
                "id": employee.id
            })
        
        return JsonResponse({
            'success': True,
            'employees': employees_data
        })
        
    except Exception as e:
        logger.error(f"Ошибка получения сотрудников по объекту: {e}")
        return JsonResponse({
            'success': False,
            'error': str(e)
        })