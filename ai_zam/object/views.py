from django.shortcuts import render, get_object_or_404
from django.db.models import Sum, Count, F
from .models import Objekt, ResursyPoObjektu, RaskhodResursa, Resurs, Kadry, FakticheskijResursPoObjektu

def home(request):
    # Получаем статистику для главной страницы
    total_objects = Objekt.objects.count()
    active_objects = Objekt.objects.filter(status='в работе').count()
    completed_objects = Objekt.objects.filter(status='завершён').count()
    
    # Статистика по ресурсам
    total_resources = ResursyPoObjektu.objects.count()
    total_cost = ResursyPoObjektu.objects.aggregate(total=Sum(F('kolichestvo') * F('cena')))['total'] or 0
    
    # Статистика по кадрам
    total_staff = Kadry.objects.count()
    
    # Последние объекты
    recent_objects = Objekt.objects.order_by('-id')[:5]
    
    context = {
        'total_objects': total_objects,
        'active_objects': active_objects,
        'completed_objects': completed_objects,
        'recent_objects': recent_objects,
        'total_resources': total_resources,
        'total_cost': total_cost,
        'total_staff': total_staff,
    }
    
    return render(request, 'object/home.html', context)

def objects_list(request):
    # Отладочная информация
    print("\n\n*** objects_list view called ***\n\n")
    
    objects = Objekt.objects.select_related('otvetstvennyj').all()
    
    # Добавляем краткую информацию для каждого объекта
    objects_with_info = []
    for obj in objects:
        total_resources = ResursyPoObjektu.objects.filter(objekt=obj).count()
        total_cost = sum(r.kolichestvo * r.cena for r in ResursyPoObjektu.objects.filter(objekt=obj))
        
        objects_with_info.append({
            'object': obj,
            'total_resources': total_resources,
            'total_cost': total_cost,
        })
    
    context = {
        'objects_with_info': objects_with_info,
    }
    
    return render(request, 'object/objects_list.html', context)

from datetime import datetime, timedelta

def object_detail(request, object_id):
    # Получаем объект или 404
    obj = get_object_or_404(Objekt.objects.select_related('otvetstvennyj'), id=object_id)
    
    # Получаем ресурсы по объекту
    resources = ResursyPoObjektu.objects.filter(objekt=obj).select_related('resurs', 'resurs__kategoriya_resursa')
    
    # Суммарная стоимость ресурсов
    total_cost = sum(r.kolichestvo * r.cena for r in resources)
    
    # Фактические расходы ресурсов
    fakticheskij_resursy = FakticheskijResursPoObjektu.objects.filter(
        resurs_po_objektu__objekt=obj
    ).select_related('resurs_po_objektu', 'resurs_po_objektu__resurs')
    
    # Расходы по фактическим ресурсам
    raskhody = {}
    all_dates = set()
    
    for fr in fakticheskij_resursy:
        rashody_list = RaskhodResursa.objects.filter(fakticheskij_resurs=fr).order_by('-data')
        raskhody[fr.id] = rashody_list
        
        # Собираем все даты расходов
        for rashod in rashody_list:
            all_dates.add(rashod.data)
    
    # Сортируем даты в обратном порядке (новые сначала)
    days = sorted(list(all_dates), reverse=True)[:6]  # Последние 6 дней
    
    # Если нет дат, создаем тестовые даты для примера
    if not days:
        today = datetime(2025, 6, 28).date()  # Используем дату из примера
        days = [today - timedelta(days=i) for i in range(6)]
    
    # Суммарный фактический расход
    total_spent = 0
    for fr_id, rr_list in raskhody.items():
        fr = FakticheskijResursPoObjektu.objects.get(id=fr_id)
        resource_cost = fr.resurs_po_objektu.cena
        total_spent += sum(rr.izraskhodovano * resource_cost for rr in rr_list)
    
    context = {
        'object': obj,
        'resources': resources,
        'total_cost': total_cost,
        'fakticheskij_resursy': fakticheskij_resursy,
        'raskhody': raskhody,
        'total_spent': total_spent,
        'days': days,
    }
    
    return render(request, 'object/object_detail.html', context)

