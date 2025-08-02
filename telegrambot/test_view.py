from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
import json
import logging

logger = logging.getLogger(__name__)

@csrf_exempt
@require_POST
def test_save_hours(request):
    """Тестовая функция для проверки записи часов"""
    logger.info("=== ТЕСТОВАЯ ФУНКЦИЯ test_save_hours ВЫЗВАНА ===")
    
    try:
        data = json.loads(request.body)
        logger.info(f"Получены данные: {data}")
        
        # Импортируем модели
        from sotrudniki.models import Sotrudnik, SotrudnikiZarplaty
        from object.models import Objekt
        from datetime import date
        
        # Получаем первого сотрудника и первый объект для теста
        sotrudnik = Sotrudnik.objects.first()
        objekt = Objekt.objects.first()
        
        if not sotrudnik or not objekt:
            return JsonResponse({
                'success': False,
                'error': 'Нет сотрудников или объектов в базе данных'
            })
        
        # Создаем тестовую запись
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
        
        logger.info(f"{'Создана' if created else 'Обновлена'} запись с ID: {zarplata.id}")
        
        return JsonResponse({
            'success': True,
            'message': f'Тестовая запись {"создана" if created else "обновлена"} с ID: {zarplata.id}',
            'sotrudnik': sotrudnik.fio,
            'objekt': objekt.nazvanie
        })
        
    except Exception as e:
        logger.error(f"Ошибка в тестовой функции: {e}")
        import traceback
        logger.error(f"Traceback: {traceback.format_exc()}")
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)