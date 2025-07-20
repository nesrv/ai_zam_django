from django.http import JsonResponse, HttpResponse
from django.views.decorators.csrf import csrf_exempt
from .models import Objekt, ResursyPoObjektu, FakticheskijResursPoObjektu, RaskhodResursa
from sotrudniki.models import Sotrudnik, Specialnost, SotrudnikiZarplaty
from django.shortcuts import get_object_or_404, render
from django.db.models import Sum
import json
from datetime import datetime

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


def get_salary_data(request, object_id):
    """API-эндпоинт для получения данных о зарплате сотрудников из таблицы sotrudniki_zarplaty"""
    try:
        # Получаем параметры из запроса
        position = request.GET.get('position', '')
        date_str = request.GET.get('date', '')
        
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
        
        # Получаем сотрудников по должности
        # Находим специальности, подходящие по названию
        specialnosti = Specialnost.objects.filter(nazvanie__icontains=position)
        
        # Если не нашли специальность, ищем по части слова
        if not specialnosti.exists() and position:
            words = position.split()
            for word in words:
                if len(word) > 3:  # Ищем только по словам длиннее 3 символов
                    specialnosti = specialnosti | Specialnost.objects.filter(nazvanie__icontains=word)
        
        # Получаем всех сотрудников объекта
        employees = objekt.sotrudniki.all()
        
        # Фильтруем по специальностям, если они найдены
        filtered_employees = []
        if specialnosti.exists():
            for spec in specialnosti:
                filtered_employees.extend(employees.filter(specialnost=spec))
        else:
            filtered_employees = list(employees)
        
        # Получаем данные о зарплате из таблицы sotrudniki_zarplaty
        employees_data = []
        
        # Сначала получаем все записи из таблицы sotrudniki_zarplaty для данного объекта и даты
        if date_obj:
            salary_records = SotrudnikiZarplaty.objects.filter(
                objekt=objekt,
                data=date_obj
            )
            print(f"Найдено {salary_records.count()} записей в таблице sotrudniki_zarplaty для даты {date_obj}")
            
            # Получаем сумму часов для этой должности и даты
            # Находим ресурс с указанной должностью
            resource = ResursyPoObjektu.objects.filter(
                objekt=objekt,
                resurs__naimenovanie__icontains=position
            ).first()
            
            # Если не нашли по точному совпадению, ищем по частичному
            if not resource:
                resources = ResursyPoObjektu.objects.filter(
                    objekt=objekt,
                    resurs__kategoriya_resursa__nazvanie__icontains="Кадровое"
                )
                
                for res in resources:
                    if position.lower() in res.resurs.naimenovanie.lower() or res.resurs.naimenovanie.lower() in position.lower():
                        resource = res
                        break
            
            # Получаем сумму часов из таблицы RaskhodResursa
            total_hours = 0
            if resource:
                fakticheskij_resurs = FakticheskijResursPoObjektu.objects.filter(
                    resurs_po_objektu=resource
                ).first()
                
                if fakticheskij_resurs:
                    raskhod = RaskhodResursa.objects.filter(
                        fakticheskij_resurs=fakticheskij_resurs,
                        data=date_obj
                    ).first()
                    
                    if raskhod:
                        total_hours = float(raskhod.izraskhodovano)
                        print(f"Найдено {total_hours} часов в таблице RaskhodResursa для должности {position} на дату {date_obj}")
        else:
            salary_records = []
            print("Дата не определена, записи из таблицы sotrudniki_zarplaty не загружены")
        
        # Создаем словарь для быстрого доступа к записям по ID сотрудника
        salary_dict = {record.sotrudnik_id: record for record in salary_records}
        
        # Выводим информацию о найденных записях в таблице sotrudniki_zarplaty
        print("Найден в таблице sotrudniki_zarplaty:")
        for record in salary_records:
            print(f"ID сотрудника: {record.sotrudnik_id}")
            print(f"Отработано часов: {record.kolichestvo_chasov}")
            print(f"KPI: {record.kpi}")
            print(f"FIO: {record.sotrudnik.fio if record.sotrudnik else 'Неизвестно'}")
            print("---")
        
        # Для каждого сотрудника проверяем наличие записи в таблице sotrudniki_zarplaty
        for employee in filtered_employees:
            # Ищем запись в словаре
            salary_data = salary_dict.get(employee.id)
            
            # Формируем данные о сотруднике
            employee_data = {
                'id': employee.id,
                'fio': employee.fio,
                'organizaciya': employee.organizaciya.nazvanie if employee.organizaciya else None,
                'podrazdelenie': employee.podrazdelenie.nazvanie if employee.podrazdelenie else None,
                'specialnost': employee.specialnost.nazvanie if employee.specialnost else None,
                'hours': float(salary_data.kolichestvo_chasov) if salary_data else 8,
                'kpi': float(salary_data.kpi) if salary_data else 1.0
            }
            
            employees_data.append(employee_data)
        
        # Если нет сотрудников с подходящей специальностью, но есть записи в таблице sotrudniki_zarplaty,
        # добавляем эти записи в список сотрудников
        if not employees_data and salary_records:
            for salary_record in salary_records:
                try:
                    employee = salary_record.sotrudnik
                    # Проверяем, соответствует ли специальность сотрудника указанной должности
                    if employee.specialnost and position.lower() in employee.specialnost.nazvanie.lower():
                        employee_data = {
                            'id': employee.id,
                            'fio': employee.fio,
                            'organizaciya': employee.organizaciya.nazvanie if employee.organizaciya else None,
                            'podrazdelenie': employee.podrazdelenie.nazvanie if employee.podrazdelenie else None,
                            'specialnost': employee.specialnost.nazvanie if employee.specialnost else None,
                            'hours': float(salary_record.kolichestvo_chasov),
                            'kpi': float(salary_record.kpi)
                        }
                        employees_data.append(employee_data)
                except Exception as e:
                    print(f"Ошибка при обработке записи зарплаты: {str(e)}")
        
        print(f"Итого найдено {len(employees_data)} сотрудников для отображения")
        
        # Если в ячейке отображается 80 часов, а в модальном окне 8 часов на сотрудника,
        # значит в ячейке отображается сумма часов всех сотрудников
        # Проверяем, что часы в модальном окне соответствуют часам в ячейке
        total_hours_in_records = 0
        if employees_data:
            # Получаем сумму часов из записей сотрудников
            total_hours_in_records = sum(emp['hours'] for emp in employees_data)
        
        return JsonResponse({
            'success': True,
            'employees': employees_data,
            'position': position,
            'date': date_str,
            'total_hours': total_hours_in_records
        })
    except Exception as e:
        print(f"Ошибка получения данных о зарплате: {str(e)}")
        return JsonResponse({'success': False, 'error': str(e)})
