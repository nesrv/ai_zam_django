from django.shortcuts import render, get_object_or_404, redirect
from .models import Objekt, ResursyPoObjektu, Resurs, FakticheskijResursPoObjektu, KategoriyaResursa

def edit_object(request, object_id):
    from sotrudniki.models import Sotrudnik, Podrazdelenie, Organizaciya
    
    obj = get_object_or_404(Objekt, id=object_id)
    
    if request.method == 'POST':
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
            
            # Удаляем неиспользуемые ресурсы
            for er in existing_resources:
                if er.id not in updated_resources:
                    er.delete()
            
            # Обрабатываем сотрудников - обновляем связи в таблице sotrudniki_sotrudnik_objekty
            selected_employees = request.POST.getlist('selected_employees[]')
            
            # Очищаем старые связи и добавляем новые
            obj.sotrudniki.clear()
            
            # Добавляем новые связи через ManyToMany поле
            for emp_id in selected_employees:
                if emp_id and emp_id.strip():
                    try:
                        emp = Sotrudnik.objects.get(id=int(emp_id))
                        obj.sotrudniki.add(emp)
                    except (Sotrudnik.DoesNotExist, ValueError):
                        pass
            
            # Перенаправляем на страницу объекта
            return redirect('object_detail', object_id=obj.id)
    
    sotrudniki = Sotrudnik.objects.select_related('specialnost').all()
    podrazdeleniya = Podrazdelenie.objects.all()
    
    expense_categories = KategoriyaResursa.objects.filter(raskhod_dokhod=True)
    income_categories = KategoriyaResursa.objects.filter(raskhod_dokhod=False)
    
    existing_resources = ResursyPoObjektu.objects.filter(objekt=obj).select_related('resurs', 'resurs__kategoriya_resursa')
    
    # Добавляем вычисленную стоимость к каждому ресурсу
    for resource in existing_resources:
        resource.total_cost = float(resource.kolichestvo) * float(resource.cena)
    
    existing_expense_resources = [r for r in existing_resources if r.resurs.kategoriya_resursa.raskhod_dokhod]
    existing_income_resources = [r for r in existing_resources if not r.resurs.kategoriya_resursa.raskhod_dokhod]
    
    # Получаем сотрудников по объекту из таблицы sotrudniki_sotrudnik через связь sotrudniki_sotrudnik_objekty
    from collections import defaultdict
    from sotrudniki.models import Specialnost
    
    # Получаем сотрудников, привязанных к объекту через ManyToMany поле
    current_employees = Sotrudnik.objects.filter(objekty=obj).select_related('specialnost')
    employees_by_specialty = defaultdict(list)
    
    # Группируем текущих сотрудников по специальностям
    for emp in current_employees:
        specialty_name = emp.specialnost.nazvanie if emp.specialnost else 'Без специальности'
        employees_by_specialty[specialty_name].append(emp)
    
    # Получаем все специальности из таблицы sotrudniki_specialnost
    all_specialties = Specialnost.objects.all()
    
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
    
    context = {
        'object': obj,
        'sotrudniki': sotrudniki,
        'podrazdeleniya': podrazdeleniya,
        'expense_categories': list(expense_categories),
        'income_categories': list(income_categories),
        'existing_expense_resources': existing_expense_resources,
        'existing_income_resources': existing_income_resources,
        'employees_by_specialty': dict(employees_by_specialty),
        'all_employees_by_specialty': dict(all_employees_by_specialty),
        'current_employees': list(current_employees),
        'debug_employees_count': current_employees.count(),
        'debug_total_employees': Sotrudnik.objects.count(),
        'debug_specialties_count': all_specialties.count(),
        'is_edit': True,
    }
    
    return render(request, 'object/edit_object.html', context)