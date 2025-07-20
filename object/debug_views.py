from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from .models import Objekt
from sotrudniki.models import Sotrudnik, Specialnost, SotrudnikiZarplaty
from django.shortcuts import get_object_or_404
from datetime import datetime

@csrf_exempt
def debug_salary_data(request, object_id):
    """Отладочный эндпоинт для вывода информации о сотрудниках в терминал"""
    try:
        # Получаем параметры из запроса
        position = request.GET.get('position', '')
        date_str = request.GET.get('date', '')
        
        # Выводим информацию в терминал
        print(f"\n[DEBUG] Информация о ячейке:")
        print(f"ID объекта: {object_id}")
        print(f"Должность: {position}")
        print(f"Дата: {date_str}")
        
        # Преобразуем дату из формата DD.MM в YYYY-MM-DD
        date_obj = None
        if date_str and date_str.strip():
            try:
                # Проверяем разные форматы даты
                if '.' in date_str:
                    # Формат DD.MM
                    parts = date_str.split('.')
                    if len(parts) == 2:
                        day, month = parts
                        year = datetime.now().year
                        date_obj = datetime.strptime(f"{year}-{month}-{day}", '%Y-%m-%d').date()
                    elif len(parts) == 3:
                        day, month, year = parts
                        if len(year) == 2:
                            year = f"20{year}"
                        date_obj = datetime.strptime(f"{year}-{month}-{day}", '%Y-%m-%d').date()
                elif '-' in date_str:
                    # Формат YYYY-MM-DD
                    date_obj = datetime.strptime(date_str, '%Y-%m-%d').date()
                elif '/' in date_str:
                    # Формат DD/MM
                    day, month = date_str.split('/')
                    year = datetime.now().year
                    date_obj = datetime.strptime(f"{year}-{month}-{day}", '%Y-%m-%d').date()
            except Exception as e:
                print(f"Ошибка преобразования даты: {e}")
                date_obj = None
        
        # Получаем объект
        objekt = get_object_or_404(Objekt, id=object_id)
        
        # Получаем записи из таблицы sotrudniki_zarplaty
        if date_obj:
            salary_records = SotrudnikiZarplaty.objects.filter(
                objekt=objekt,
                data=date_obj
            )
            
            # Выводим информацию о найденных записях
            print("Найден в таблице sotrudniki_zarplaty:")
            for record in salary_records:
                print(f"ID сотрудника: {record.sotrudnik_id}")
                print(f"Отработано часов: {record.kolichestvo_chasov}")
                print(f"KPI: {record.kpi}")
                print(f"FIO: {record.sotrudnik.fio if record.sotrudnik else 'Неизвестно'}")
                print("---")
        else:
            print("Дата не определена, записи из таблицы sotrudniki_zarplaty не загружены")
        
        # Возвращаем успешный ответ
        return JsonResponse({
            'success': True, 
            'message': 'Информация выведена в терминал',
            'debug_info': {
                'object_id': object_id,
                'position': position,
                'date': date_str
            }
        })
    except Exception as e:
        print(f"[ERROR] Ошибка в отладочном эндпоинте: {str(e)}")
        return JsonResponse({'success': False, 'error': str(e)})