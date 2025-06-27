from django.shortcuts import render, get_object_or_404
from django.db.models import Sum, Count, F
from .models import Objekt, ResursyPoObjektu, RaskhodResursa, Resurs, Kadry, FakticheskijResursPoObjektu
from datetime import datetime, timedelta
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
import json
import matplotlib
matplotlib.use('Agg')  # Используем backend без GUI
import matplotlib.pyplot as plt
import os
from django.conf import settings

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
    
    # Создаем дни точно так же, как в object_detail
    today = datetime.now().date()
    days = [today - timedelta(days=i) for i in range(20)]
    
    # Добавляем краткую информацию для каждого объекта
    objects_with_info = []
    total_budget = 0.0
    total_completed = 0.0
    
    # Словарь для итоговых сумм по дням
    total_daily_expenses = {}
    
    for obj in objects:
        # Планируемые ресурсы - используем точно такой же метод, как в object_detail
        planned_resources = ResursyPoObjektu.objects.filter(objekt=obj).select_related('resurs', 'resurs__kategoriya_resursa')
        
        # Вычисляем общую стоимость точно так же, как в object_detail
        total_cost = sum(float(r.kolichestvo * r.cena) for r in planned_resources)
        
        # Фактические расходы
        fakticheskij_resursy = FakticheskijResursPoObjektu.objects.filter(
            resurs_po_objektu__objekt=obj
        )
        
        completed_cost = 0.0
        daily_expenses = {}  # Словарь для хранения расходов по дням
        
        for fr in fakticheskij_resursy:
            rashody = RaskhodResursa.objects.filter(fakticheskij_resurs=fr)
            resource_cost = float(fr.resurs_po_objektu.cena)
            
            for rr in rashody:
                # Умножаем фактический расход на запланированную цену
                izraskhodovano = float(rr.izraskhodovano)
                expense_amount = izraskhodovano * resource_cost
                completed_cost += expense_amount
                
                # Сохраняем расход по дням
                date_key = rr.data.strftime('%Y-%m-%d')
                if date_key not in daily_expenses:
                    daily_expenses[date_key] = 0.0
                daily_expenses[date_key] += expense_amount
                
                # Добавляем в общие итоги по дням
                if date_key not in total_daily_expenses:
                    total_daily_expenses[date_key] = 0.0
                total_daily_expenses[date_key] += expense_amount
        
        # Бюджет доходов и расходов (разность между планируемыми и фактическими)
        budget_balance = total_cost - completed_cost
        
        objects_with_info.append({
            'object': obj,
            'total_cost': total_cost,
            'completed_cost': completed_cost,
            'budget_balance': budget_balance,
            'daily_expenses': daily_expenses,
        })
        
        total_budget += total_cost
        total_completed += completed_cost
    
    # Создаем графики
    chart_path = create_profit_balance_charts(objects_with_info, days)
    
    context = {
        'objects_with_info': objects_with_info,
        'days': days,
        'total_budget': total_budget,
        'total_completed': total_completed,
        'total_balance': total_budget - total_completed,
        'total_daily_expenses': total_daily_expenses,
        'chart_path': chart_path if chart_path else None,
    }
    
    return render(request, 'object/objects_list.html', context)

def create_profit_balance_charts(objects_with_info, days):
    """Создает график баланса прибыли по объектам по дням"""
    try:
        # Проверяем, есть ли данные для графиков
        if not objects_with_info:
            print("Нет данных для создания графиков")
            return None
            
        # Настройка стиля для темной темы
        plt.style.use('dark_background')
        
        # Создаем один график
        fig, ax = plt.subplots(1, 1, figsize=(16, 8))
        fig.patch.set_facecolor('#1a1a1a')
        
        # Подготавливаем данные для графика
        day_labels = [day.strftime('%d.%m') for day in days]
        x = range(len(day_labels))
        
        # Создаем линии для каждого объекта
        colors = ['#3498db', '#e74c3c', '#2ecc71', '#f39c12', '#9b59b6', '#1abc9c', '#e67e22', '#34495e']
        
        # Собираем данные для итоговой линии
        total_by_day = [0] * len(days)
        
        for i, item in enumerate(objects_with_info):
            object_name = item['object'].nazvanie
            daily_expenses = item['daily_expenses']
            
            # Создаем данные по дням для этого объекта
            y_values = []
            for j, day in enumerate(days):
                day_key = day.strftime('%Y-%m-%d')
                expense = float(daily_expenses.get(day_key, 0))
                y_values.append(expense)
                total_by_day[j] += expense
            
            # Рисуем линию для объекта
            color = colors[i % len(colors)]
            line = ax.plot(x, y_values, 'o-', linewidth=2, markersize=6, label=object_name, color=color, alpha=0.8)
            
            # Добавляем подписи к линиям (последняя точка)
            if y_values:
                last_value = y_values[-1]
                ax.annotate(f'{object_name}: {int(last_value):,}₽', 
                           xy=(x[-1], last_value), 
                           xytext=(x[-1] + 0.5, last_value),
                           fontsize=9, color=color, weight='bold',
                           bbox=dict(boxstyle='round,pad=0.3', facecolor='black', alpha=0.7),
                           arrowprops=dict(arrowstyle='->', color=color, alpha=0.7))
        
        # Рисуем итоговую линию
        ax.plot(x, total_by_day, 's-', linewidth=4, markersize=10, label='ИТОГО', color='#ffffff', alpha=1.0)
        
        # Подпись для итоговой линии
        if total_by_day:
            last_total = total_by_day[-1]
            ax.annotate(f'ИТОГО: {int(last_total):,}₽', 
                       xy=(x[-1], last_total), 
                       xytext=(x[-1] + 0.5, last_total + max(total_by_day) * 0.1),
                       fontsize=12, color='#ffffff', weight='bold',
                       bbox=dict(boxstyle='round,pad=0.5', facecolor='#2c3e50', alpha=0.9),
                       arrowprops=dict(arrowstyle='->', color='#ffffff', alpha=0.9))
        
        ax.set_xlabel('Дни', fontsize=12, color='white')
        ax.set_ylabel('Расходы (₽)', fontsize=12, color='white')
        ax.set_title('Расходы по объектам по дням', fontsize=14, color='white', pad=20)
        ax.set_xticks(x)
        ax.set_xticklabels(day_labels, rotation=45, ha='right', fontsize=10)
        ax.legend(bbox_to_anchor=(1.05, 1), loc='upper left')
        ax.grid(True, alpha=0.3)
        
        # Настройка внешнего вида
        plt.tight_layout()
        
        # Сохраняем график
        charts_dir = os.path.join(settings.BASE_DIR, 'static', 'charts')
        os.makedirs(charts_dir, exist_ok=True)
        chart_path = os.path.join(charts_dir, 'profit_balance_chart.png')
        
        plt.savefig(chart_path, dpi=300, bbox_inches='tight', facecolor='#1a1a1a')
        plt.close()
        
        # Проверяем, что файл создался
        if os.path.exists(chart_path):
            print(f"График успешно создан: {chart_path}")
        else:
            print(f"Ошибка: файл не создан: {chart_path}")
        
        return 'charts/profit_balance_chart.png'
    except Exception as e:
        print(f"Ошибка при создании графиков: {e}")
        return None

def object_detail(request, object_id):
    # Получаем объект или 404
    obj = get_object_or_404(Objekt.objects.select_related('otvetstvennyj'), id=object_id)
    
    # Получаем ресурсы по объекту
    resources = ResursyPoObjektu.objects.filter(objekt=obj).select_related('resurs', 'resurs__kategoriya_resursa')
    
    # Суммарная стоимость ресурсов
    total_cost = sum(float(r.kolichestvo * r.cena) for r in resources)
    
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
    
    # Всегда создаем 20 дней для отображения
    today = datetime.now().date()
    days = [today - timedelta(days=i) for i in range(20)]
    
    # Суммарный фактический расход
    total_spent = 0.0
    for fr_id, rr_list in raskhody.items():
        fr = FakticheskijResursPoObjektu.objects.get(id=fr_id)
        resource_cost = float(fr.resurs_po_objektu.cena)
        total_spent += sum(float(rr.izraskhodovano) * resource_cost for rr in rr_list)
    
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

@csrf_exempt
@require_POST
def update_expense(request):
    try:
        data = json.loads(request.body)
        resource_id = data.get('resource_id')
        date_str = data.get('date')
        amount = float(data.get('amount', 0))
        
        # Получаем ресурс по объекту
        resource = ResursyPoObjektu.objects.get(id=resource_id)
        
        # Получаем или создаем фактический ресурс
        fakticheskij_resurs, created = FakticheskijResursPoObjektu.objects.get_or_create(
            resurs_po_objektu=resource
        )
        
        # Парсим дату
        date_obj = datetime.strptime(date_str, '%Y-%m-%d').date()
        
        # Обновляем или создаем расход
        rashod, created = RaskhodResursa.objects.update_or_create(
            fakticheskij_resurs=fakticheskij_resurs,
            data=date_obj,
            defaults={'izraskhodovano': amount}
        )
        
        # Пересчитываем общую сумму потраченного для ресурса
        total_spent = RaskhodResursa.objects.filter(
            fakticheskij_resurs=fakticheskij_resurs
        ).aggregate(total=Sum('izraskhodovano'))['total'] or 0
        
        # Обновляем поле potracheno в resursy_po_objektu
        resource.potracheno = total_spent
        resource.save()
        
        return JsonResponse({
            'success': True,
            'potracheno': float(total_spent),
            'ostatok': float(resource.kolichestvo - total_spent)
        })
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)})

@csrf_exempt
@require_POST
def update_resource_data(request):
    try:
        data = json.loads(request.body)
        resource_id = data.get('resource_id')
        field_type = data.get('field_type')  # 'kolichestvo' или 'cena'
        new_value = float(data.get('value', 0))
        
        # Получаем ресурс по объекту
        resource = ResursyPoObjektu.objects.get(id=resource_id)
        
        # Обновляем соответствующее поле
        if field_type == 'kolichestvo':
            resource.kolichestvo = new_value
        elif field_type == 'cena':
            resource.cena = new_value
        else:
            return JsonResponse({'success': False, 'error': 'Неверный тип поля'})
        
        resource.save()
        
        # Пересчитываем сумму
        new_sum = resource.kolichestvo * resource.cena
        
        return JsonResponse({
            'success': True,
            'new_sum': float(new_sum),
            'ostatok': float(resource.kolichestvo - resource.potracheno)
        })
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)})

