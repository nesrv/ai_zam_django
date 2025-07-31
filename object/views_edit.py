from django.shortcuts import render, get_object_or_404, redirect
from collections import defaultdict
from .models import Objekt, ResursyPoObjektu, Resurs, FakticheskijResursPoObjektu, KategoriyaResursa

def edit_object(request, object_id):
    from sotrudniki.models import Sotrudnik, Podrazdelenie, Organizaciya
    
    obj = get_object_or_404(Objekt, id=object_id)
    
    if request.method == 'POST':
        print(f"POST: {dict(request.POST)}")
        print(f"Employees: {request.POST.getlist('selected_employees[]')}")
        organizaciya_name = request.POST.get('organizaciya')
        nazvanie = request.POST.get('nazvanie')
        data_nachala = request.POST.get('data_nachala')
        
        if nazvanie and data_nachala:
            obj.nazvanie = nazvanie
            obj.data_nachala = data_nachala
            
            if organizaciya_name:
                try:
                    organizaciya = Organizaciya.objects.get(nazvanie=organizaciya_name)
                except Organizaciya.DoesNotExist:
                    import random
                    unique_inn = f"{random.randint(1000000000, 9999999999)}"
                    organizaciya = Organizaciya.objects.create(
                        nazvanie=organizaciya_name,
                        inn=unique_inn,
                        is_active=True
                    )
                obj.organizaciya = organizaciya
            
            obj.save()
            
            # Просто обновляем основные поля ресурсов без удаления фактических данных
            existing_resources = list(ResursyPoObjektu.objects.filter(objekt=obj))
            
            # Обновляем существующие ресурсы
            updated_resources = set()
            
            # Получаем данные из формы
            expense_resources = request.POST.getlist('expense_resource[]')
            expense_quantities = request.POST.getlist('expense_quantity[]')
            expense_prices = request.POST.getlist('expense_price[]')
            income_resources = request.POST.getlist('income_resource[]')
            income_quantities = request.POST.getlist('income_quantity[]')
            income_prices = request.POST.getlist('income_price[]')
            
            # Обрабатываем расходные ресурсы
            for i, resource_id in enumerate(expense_resources):
                if resource_id and i < len(expense_quantities) and i < len(expense_prices):
                    if expense_quantities[i] and expense_prices[i]:
                        resurs = Resurs.objects.get(id=resource_id)
                        
                        # Ищем существующий ресурс
                        existing = None
                        for er in existing_resources:
                            if er.resurs.id == int(resource_id):
                                existing = er
                                break
                        
                        if existing:
                            # Обновляем существующий
                            existing.kolichestvo = float(expense_quantities[i])
                            existing.cena = float(expense_prices[i])
                            existing.save()
                            updated_resources.add(existing.id)
                        else:
                            # Создаем новый
                            new_resource = ResursyPoObjektu.objects.create(
                                objekt=obj,
                                resurs=resurs,
                                kolichestvo=float(expense_quantities[i]),
                                cena=float(expense_prices[i])
                            )
                            FakticheskijResursPoObjektu.objects.create(resurs_po_objektu=new_resource)
                            updated_resources.add(new_resource.id)
            
            # Обрабатываем доходные ресурсы
            for i, resource_id in enumerate(income_resources):
                if resource_id and i < len(income_quantities) and i < len(income_prices):
                    if income_quantities[i] and income_prices[i]:
                        try:
                            resurs = Resurs.objects.get(id=resource_id)
                            
                            # Ищем существующий ресурс
                            existing = None
                            for er in existing_resources:
                                if er.resurs.id == int(resource_id):
                                    existing = er
                                    break
                            
                            if existing:
                                # Обновляем существующий
                                existing.kolichestvo = float(income_quantities[i])
                                existing.cena = float(income_prices[i])
                                existing.save()
                                updated_resources.add(existing.id)
                            else:
                                # Создаем новый
                                new_resource = ResursyPoObjektu.objects.create(
                                    objekt=obj,
                                    resurs=resurs,
                                    kolichestvo=float(income_quantities[i]),
                                    cena=float(income_prices[i])
                                )
                                FakticheskijResursPoObjektu.objects.create(resurs_po_objektu=new_resource)
                                updated_resources.add(new_resource.id)
                        except Resurs.DoesNotExist:
                            print(f"Ресурс с ID {resource_id} не найден")
                            continue
            
            # Удаляем неиспользуемые ресурсы
            for er in existing_resources:
                if er.id not in updated_resources:
                    er.delete()
            
            # Обрабатываем сотрудников
            selected_employees = request.POST.getlist('selected_employees[]')
            print(f"Selected employees: {selected_employees}")
            
            # Очищаем текущие связи объекта с сотрудниками
            obj.sotrudniki.clear()
            
            # Добавляем новые связи для каждого выбранного сотрудника
            added_employees = 0
            failed_employees = []
            
            # Удаляем дубликаты из списка сотрудников
            unique_employees = list(set(selected_employees))
            print(f"Unique employees: {unique_employees}")
            
            # Создаем список сотрудников для массового добавления
            employees_to_add = []
            
            for emp_id in unique_employees:
                if emp_id:
                    try:
                        emp = Sotrudnik.objects.get(id=int(emp_id))
                        employees_to_add.append(emp)
                        added_employees += 1
                    except Sotrudnik.DoesNotExist:
                        print(f"Error: Сотрудник с ID {emp_id} не найден")
                        failed_employees.append(emp_id)
                    except Exception as e:
                        print(f"Error processing employee {emp_id}: {str(e)}")
                        failed_employees.append(emp_id)
            
            # Массовое добавление сотрудников
            if employees_to_add:
                try:
                    obj.sotrudniki.add(*employees_to_add)
                    print(f"Added {len(employees_to_add)} employees to object {obj.id} using bulk add")
                except Exception as e:
                    print(f"Error during bulk add: {str(e)}")
                    # Если массовое добавление не удалось, пробуем по одному
                    for emp in employees_to_add:
                        try:
                            obj.sotrudniki.add(emp)
                            print(f"Added employee {emp.id} individually")
                        except Exception as e2:
                            print(f"Error adding employee {emp.id} individually: {str(e2)}")
                            failed_employees.append(str(emp.id))
            
            # Проверяем, что связи созданы успешно
            actual_employees = obj.sotrudniki.count()
            print(f"Actual employees count after save: {actual_employees}")
            if actual_employees != added_employees:
                print(f"Warning: Не все сотрудники были добавлены к объекту")
                print(f"Failed employees: {failed_employees}")
            
            # Проверяем сотрудников, которые были добавлены
            added_employee_ids = [str(emp.id) for emp in obj.sotrudniki.all()]
            print(f"Successfully added employee IDs: {added_employee_ids}")
            
            # Проверяем, есть ли в списке конкретный сотрудник
            if selected_employees and len(selected_employees) == 1:
                check_emp_id = selected_employees[0]
                if check_emp_id in added_employee_ids:
                    print(f"Employee {check_emp_id} was successfully added to the object")
                else:
                    print(f"WARNING: Employee {check_emp_id} was NOT added to the object!")
                    # Пробуем добавить еще раз
                    try:
                        emp = Sotrudnik.objects.get(id=int(check_emp_id))
                        obj.sotrudniki.add(emp)
                        print(f"Retry: Successfully added employee {check_emp_id}")
                    except Exception as e:
                        print(f"Retry failed: {str(e)}")
            
            # Проверяем еще раз после всех операций
            final_count = obj.sotrudniki.count()
            print(f"Final employee count: {final_count}")
            
            # Сохраняем объект еще раз для уверенности
            obj.save()
            
            # Перенаправляем в зависимости от кнопки
            action = request.POST.get('action', 'save_and_exit')
            if action == 'save_and_stay':
                return redirect('edit_object', object_id=obj.id)
            else:
                return redirect('object_detail', object_id=obj.id)
    
    sotrudniki = Sotrudnik.objects.select_related('specialnost').all()
    podrazdeleniya = Podrazdelenie.objects.all()
    
    expense_categories = KategoriyaResursa.objects.filter(raskhod_dokhod=True)
    income_categories = KategoriyaResursa.objects.filter(raskhod_dokhod=False)
    
    existing_resources = ResursyPoObjektu.objects.filter(objekt=obj).select_related('resurs', 'resurs__kategoriya_resursa')
    
    # Добавляем вычисленную стоимость к каждому ресурсу
    for resource in existing_resources:
        resource.total_cost = float(resource.kolichestvo) * float(resource.cena)
    
    # Группируем ресурсы по категориям
    expense_resources_by_category = defaultdict(list)
    income_resources_by_category = defaultdict(list)
    
    # Создаем словарь для должностей из Кадрового обеспечения
    kadrovoe_positions = defaultdict(dict)
    
    for resource in existing_resources:
        category_name = resource.resurs.kategoriya_resursa.nazvanie
        if resource.resurs.kategoriya_resursa.raskhod_dokhod:
            expense_resources_by_category[category_name].append(resource)
            
            # Если это Кадровое обеспечение, сохраняем должность и количество
            if category_name == "Кадровое обеспечение":
                position_name = resource.resurs.naimenovanie
                kadrovoe_positions[position_name] = {
                    'quantity': resource.kolichestvo,
                    'price': resource.cena,
                    'employees': []
                }
        else:
            income_resources_by_category[category_name].append(resource)
    
    existing_expense_resources = dict(expense_resources_by_category)
    existing_income_resources = dict(income_resources_by_category)
    
    # Получаем сотрудников объекта
    current_employees = obj.sotrudniki.select_related('specialnost').all()
    employees_by_specialty = defaultdict(list)
    
    from sotrudniki.models import Specialnost
    
    # Получаем все специальности из таблицы sotrudniki_specialnost
    all_specialties = Specialnost.objects.all()
    
    # Заполняем категории специальностей, если они не заполнены
    construction_specialties = [
        'Альпинист', 'Газорезчик', 'Сварщик', 'Монтажник', 'Стропальщик',
        'Бетонщик', 'Арматурщик', 'Плотник', 'Электрик'
    ]
    
    for specialty in all_specialties:
        if specialty.nazvanie in construction_specialties and not specialty.kategoriya:
            specialty.kategoriya = '2'  # Категория 2 - Строительное управление
            specialty.save()
    
    # Получаем сотрудников объекта
    current_employees = obj.sotrudniki.select_related('specialnost').all()
    employees_by_specialty = defaultdict(list)
    
    # Группируем сотрудников
    employees_category_1 = []
    employees_category_2_by_specialty = defaultdict(list)
    employees_by_podrazdelenie = defaultdict(list)
    employees_by_position = defaultdict(list)  # Сотрудники по должностям
    
    # Получаем подразделения организации
    from sotrudniki.models import OrganizaciyaPodrazdelenie
    
    organizacii = obj.organizacii.all()
    if organizacii:
        # Берем подразделения первой организации
        podrazdeleniya = organizacii.first().podrazdeleniya.all()
    else:
        podrazdeleniya = []
    
    for emp in current_employees:
        # Группировка по специальностям
        if emp.specialnost and emp.specialnost.kategoriya == '2':
            specialty_name = emp.specialnost.nazvanie
            employees_category_2_by_specialty[specialty_name].append(emp)
        else:
            employees_category_1.append(emp)
        
        # Группировка по подразделениям
        if emp.podrazdelenie:
            podrazdelenie_name = emp.podrazdelenie.nazvanie
            employees_by_podrazdelenie[podrazdelenie_name].append(emp)
        else:
            # Если подразделение не указано, добавляем в группу "Без подразделения"
            employees_by_podrazdelenie["Без подразделения"].append(emp)
        
        # Группировка по должностям из Кадрового обеспечения
        if emp.specialnost:
            position_name = emp.specialnost.nazvanie
            # Проверяем, есть ли такая должность в Кадровом обеспечении
            if position_name in kadrovoe_positions:
                kadrovoe_positions[position_name]['employees'].append(emp)
            else:
                # Если должности нет в Кадровом обеспечении, добавляем в общий список должностей
                employees_by_position[position_name].append(emp)
        else:
            # Если специальность не указана, добавляем в группу "Без должности"
            employees_by_position["Без должности"].append(emp)
    
    # Добавляем пустые списки для всех специальностей категории 2
    for specialty in all_specialties.filter(kategoriya='2'):
        if specialty.nazvanie not in employees_category_2_by_specialty:
            employees_category_2_by_specialty[specialty.nazvanie] = []
    
    for specialty in all_specialties:
        if specialty.nazvanie in construction_specialties and not specialty.kategoriya:
            specialty.kategoriya = '2'  # Категория 2 - Строительное управление
            specialty.save()
    
    # Создаем тестовых сотрудников если их нет
    if Sotrudnik.objects.count() == 0:
        from datetime import date
        test_employees = [
            {'fio': 'Иванов Иван Иванович', 'specialty': 'Альпинист'},
            {'fio': 'Петров Петр Петрович', 'specialty': 'Газорезчик'},
            {'fio': 'Сидоров Сидор Сидорович', 'specialty': 'Производитель работ'},
        ]
        
        for emp_data in test_employees:
            specialty, _ = Specialnost.objects.get_or_create(nazvanie=emp_data['specialty'])
            Sotrudnik.objects.create(
                fio=emp_data['fio'],
                specialnost=specialty,
                data_rozhdeniya=date(1990, 1, 1),
                data_priema=date.today(),
                data_nachala_raboty=date.today()
            )
    
    # Добавляем пустые списки для специальностей без сотрудников
    for specialty in all_specialties:
        if specialty.nazvanie not in employees_by_specialty:
            employees_by_specialty[specialty.nazvanie] = []
    
    # Получаем всех сотрудников по специальностям для выпадающих списков
    all_employees_by_specialty = defaultdict(list)
    all_employees_full = Sotrudnik.objects.select_related('specialnost').all()
    for emp in all_employees_full:
        specialty_name = emp.specialnost.nazvanie if emp.specialnost else 'Без специальности'
        all_employees_by_specialty[specialty_name].append(emp)
    
    # Получаем организации авторизованного пользователя
    user_organizations = []
    if request.user.is_authenticated:
        from .models import UserProfile
        user_profile, created = UserProfile.objects.get_or_create(user=request.user)
        user_organizations = user_profile.organizations.all()
    
    context = {
        'object': obj,
        'sotrudniki': sotrudniki,
        'podrazdeleniya': podrazdeleniya,
        'expense_categories': list(expense_categories),
        'income_categories': list(income_categories),
        'existing_expense_resources': existing_expense_resources,
        'existing_income_resources': existing_income_resources,
        'employees_category_1': employees_category_1,
        'employees_category_2_by_specialty': dict(employees_category_2_by_specialty),
        'employees_by_podrazdelenie': dict(employees_by_podrazdelenie),
        'employees_by_position': dict(employees_by_position),
        'kadrovoe_positions': dict(kadrovoe_positions),
        'all_employees_by_specialty': dict(all_employees_by_specialty),
        'current_employees': list(current_employees),
        'org_podrazdeleniya': list(podrazdeleniya),
        'debug_employees_count': current_employees.count(),
        'debug_total_employees': Sotrudnik.objects.count(),
        'debug_specialties_count': all_specialties.count(),
        'user_organizations': user_organizations,
        'is_edit': True,
    }
    
    return render(request, 'object/edit_object.html', context)