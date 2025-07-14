from django.shortcuts import render, get_object_or_404, redirect
from django.db.models import Sum, Count, F
from .models import Objekt, ResursyPoObjektu, RaskhodResursa, Resurs, FakticheskijResursPoObjektu, DokhodResursa, SvodnayaRaskhodDokhodPoDnyam
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
import time

def home(request):
    # Получаем статистику для главной страницы
    total_objects = Objekt.objects.count()
    active_objects = Objekt.objects.filter(status='в работе').count()
    completed_objects = Objekt.objects.filter(status='завершён').count()
    
    # Статистика по ресурсам
    total_resources = ResursyPoObjektu.objects.count()
    total_cost = ResursyPoObjektu.objects.aggregate(total=Sum(F('kolichestvo') * F('cena')))['total'] or 0
    
    # Статистика по кадрам
    total_staff = 0  # Заглушка
    
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
    
    objects = Objekt.objects.filter(is_active=True)
    
    # Создаем дни точно так же, как в object_detail
    today = datetime.now().date()
    days = [today - timedelta(days=i) for i in range(20)]
    
    # Добавляем краткую информацию для каждого объекта
    objects_with_info = []
    total_budget = 0.0
    total_completed = 0.0
    
    # Словарь для итоговых сумм по дням (баланс)
    total_daily_balance = {}
    
    # Словари для данных доходов и расходов по дням
    daily_income_data = {}
    daily_expense_data = {}
    
    for obj in objects:
        # Планируемые ресурсы - используем точно такой же метод, как в object_detail
        planned_resources = ResursyPoObjektu.objects.filter(objekt=obj).select_related('resurs', 'resurs__kategoriya_resursa')
        
        # Вычисляем общую стоимость точно так же, как в object_detail
        total_cost = sum(float(r.kolichestvo) * float(r.cena) for r in planned_resources)
        
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
                

        
        # Получаем данные доходов (подрядные организации)
        income_resources = ResursyPoObjektu.objects.filter(
            objekt=obj,
            resurs__kategoriya_resursa__nazvanie='Подрядные организации'
        ).select_related('resurs', 'resurs__kategoriya_resursa')
        
        income_fakticheskij_resursy = FakticheskijResursPoObjektu.objects.filter(
            resurs_po_objektu__objekt=obj,
            resurs_po_objektu__resurs__kategoriya_resursa__nazvanie='Подрядные организации'
        )
        
        daily_income = {}  # Словарь для хранения доходов по дням
        
        for fr in income_fakticheskij_resursy:
            rashody = RaskhodResursa.objects.filter(fakticheskij_resurs=fr)
            resource_cost = float(fr.resurs_po_objektu.cena)
            
            for rr in rashody:
                # Умножаем фактический расход на запланированную цену
                izraskhodovano = float(rr.izraskhodovano)
                income_amount = izraskhodovano * resource_cost
                
                # Сохраняем доход по дням
                date_key = rr.data.strftime('%Y-%m-%d')
                if date_key not in daily_income:
                    daily_income[date_key] = 0.0
                daily_income[date_key] += income_amount
        
        # Бюджет доходов и расходов (разность между планируемыми и фактическими)
        budget_balance = total_cost - completed_cost
        
        # Получаем баланс по дням из сводной таблицы
        daily_balance = {}
        svodnaya_data = SvodnayaRaskhodDokhodPoDnyam.objects.filter(objekt=obj)
        for svodnaya in svodnaya_data:
            day_key = svodnaya.data.strftime('%Y-%m-%d')
            daily_balance[day_key] = float(svodnaya.balans)
        
        objects_with_info.append({
            'object': obj,
            'total_cost': total_cost,
            'completed_cost': completed_cost,
            'budget_balance': budget_balance,
            'daily_expenses': daily_expenses,
            'daily_income': daily_income,
            'daily_balance': daily_balance,
        })
        
        total_budget += total_cost
        total_completed += completed_cost
        
        # Сохраняем данные из сводной таблицы для графика
        for svodnaya in svodnaya_data:
            day_key = svodnaya.data.strftime('%Y-%m-%d')
            
            # Расходы
            if day_key not in daily_expense_data:
                daily_expense_data[day_key] = 0.0
            daily_expense_data[day_key] += float(svodnaya.raskhod)
            
            # Доходы
            if day_key not in daily_income_data:
                daily_income_data[day_key] = 0.0
            daily_income_data[day_key] += float(svodnaya.dokhod)
            
            # Баланс
            if day_key not in total_daily_balance:
                total_daily_balance[day_key] = 0.0
            total_daily_balance[day_key] += float(svodnaya.balans)
    
    # Создаем графики
    chart_path = create_profit_balance_charts(objects_with_info, days, daily_income_data, daily_expense_data)
    
    context = {
        'objects_with_info': objects_with_info,
        'days': days,
        'total_budget': total_budget,
        'total_completed': total_completed,
        'total_balance': total_budget - total_completed,
        'total_daily_balance': total_daily_balance,
        'chart_path': chart_path if chart_path else None,
    }
    
    return render(request, 'object/objects_list.html', context)

def create_profit_balance_charts(objects_with_info, days, daily_income_data, daily_expense_data):
    """Создает график баланса прибыли по объектам по дням по формуле доход-расход"""
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
        
        # Подготавливаем данные для графика из сводной таблицы
        svodnaya_all = SvodnayaRaskhodDokhodPoDnyam.objects.all().order_by('data')
        
        # Создаем словарь балансов по дням и объектам
        balance_by_date = {}  # Общий баланс
        balance_by_object = {}  # Баланс по объектам
        
        for svodnaya in svodnaya_all:
            day_key = svodnaya.data.strftime('%Y-%m-%d')
            objekt_name = svodnaya.objekt.nazvanie
            
            # Общий баланс
            if day_key not in balance_by_date:
                balance_by_date[day_key] = 0
            balance_by_date[day_key] += float(svodnaya.balans)
            
            # Баланс по объектам
            if objekt_name not in balance_by_object:
                balance_by_object[objekt_name] = {}
            balance_by_object[objekt_name][day_key] = float(svodnaya.balans)
        
        # Создаем массивы для графика
        day_labels = []
        balance_values = []  # Общий баланс
        object_lines = {}  # Линии по объектам
        
        # Инициализируем линии объектов
        for objekt_name in balance_by_object.keys():
            object_lines[objekt_name] = []
        
        for day_key in sorted(balance_by_date.keys(), reverse=True):
            from datetime import datetime
            day = datetime.strptime(day_key, '%Y-%m-%d').date()
            day_labels.append(day.strftime('%d.%m'))
            balance_values.append(balance_by_date[day_key] / 1000)
            
            # Добавляем значения для каждого объекта
            for objekt_name in balance_by_object.keys():
                value = balance_by_object[objekt_name].get(day_key, 0) / 1000
                object_lines[objekt_name].append(value)
        
        x = range(len(day_labels))
        

        
        # Рисуем общую линию баланса
        ax.plot(x, balance_values, '^-', linewidth=4, markersize=10, label='Общий баланс', color='#3498db', alpha=1.0)
        
        # Рисуем линии для первых двух объектов
        colors = ['#e74c3c', '#2ecc71', '#f39c12', '#9b59b6', '#1abc9c', '#34495e']
        for i, (objekt_name, values) in enumerate(list(object_lines.items())[:2]):
            color = colors[i % len(colors)]
            ax.plot(x, values, 'o-', linewidth=2, markersize=6, label=objekt_name, color=color, alpha=0.8)
        
        # Добавляем подписи значений для баланса
        for i, balance in enumerate(balance_values):
            # Подписи для баланса (каждая 2-я точка)
            if i % 2 == 0 and abs(balance) > 1:  # Только если баланс значимый
                ax.annotate(f'{balance:.1f} тыс.₽', 
                           xy=(i, balance), 
                           xytext=(i, balance + (10 if balance >= 0 else -10)),
                           fontsize=9, color='#3498db', weight='bold',
                           ha='center', va='bottom' if balance >= 0 else 'top',
                           bbox=dict(boxstyle='round,pad=0.3', facecolor='#2c3e50', alpha=0.8))
        
        # Добавляем подпись к последней точке баланса
        if balance_values and x:
            last_balance = balance_values[-1]
            ax.annotate(f'Баланс: {last_balance:.1f} тыс.₽', 
                       xy=(x[-1], last_balance), 
                       xytext=(x[-1] + 0.5, last_balance + 10),
                       fontsize=12, color='#3498db', weight='bold',
                       bbox=dict(boxstyle='round,pad=0.5', facecolor='#2c3e50', alpha=0.9),
                       arrowprops=dict(arrowstyle='->', color='#3498db', alpha=0.9))
        
        # Добавляем горизонтальную линию для нулевого баланса
        ax.axhline(y=0, color='#ffffff', linestyle='--', alpha=0.5, linewidth=1)
        if x:
            ax.annotate('Нулевой баланс', xy=(len(x)-1, 0), xytext=(len(x)-2, 5),
                       fontsize=10, color='#ffffff', alpha=0.7,
                       bbox=dict(boxstyle='round,pad=0.2', facecolor='black', alpha=0.5),
                       arrowprops=dict(arrowstyle='->', color='#ffffff', alpha=0.5))
        
        ax.set_xlabel('Дни', fontsize=12, color='white')
        ax.set_ylabel('Сумма (тыс. ₽)', fontsize=12, color='white')
        ax.set_title('Баланс доходов и расходов по дням (доход-расход)', fontsize=14, color='white', pad=20)
        ax.set_xticks(x)
        ax.set_xticklabels(day_labels, rotation=45, ha='right', fontsize=10)
        
        # Добавляем надписи "Прибыль" и "Расход" в углы координатной сетки
        if x:
            # Надпись "Прибыль" в левый верхний угол
            ax.text(0.5, ax.get_ylim()[1] * 0.9, 'Прибыль', fontsize=16, color='#2ecc71', weight='bold', 
                   ha='left', va='top', 
                   bbox=dict(boxstyle='round,pad=0.5', facecolor='#2c3e50', alpha=0.8))
            
            # Надпись "Расход" в правый нижний угол
            ax.text(len(x) - 0.5, ax.get_ylim()[0] * 0.9, 'Расход', fontsize=16, color='#e74c3c', weight='bold', 
                   ha='right', va='bottom',
                   bbox=dict(boxstyle='round,pad=0.5', facecolor='#2c3e50', alpha=0.8))
        
        # Форматирование оси Y в тысячах рублей
        from matplotlib.ticker import FuncFormatter
        def thousands_formatter(x, pos):
            return f'{x:.0f}'
        ax.yaxis.set_major_formatter(FuncFormatter(thousands_formatter))
        
        ax.legend(bbox_to_anchor=(1.05, 1), loc='upper left')
        ax.grid(True, alpha=0.3)
        
        # Настройка внешнего вида
        try:
            plt.tight_layout()
        except:
            # Если tight_layout не работает, используем subplots_adjust
            plt.subplots_adjust(left=0.1, right=0.85, top=0.9, bottom=0.2)
        
        # Сохраняем график в staticfiles/images
        static_dir = os.path.join(settings.STATIC_ROOT, 'images')
        os.makedirs(static_dir, exist_ok=True)
        
        # Удаляем старые файлы графиков (оставляем только последние 5)
        old_charts = [f for f in os.listdir(static_dir) if f.startswith('profit_balance_chart_')]
        old_charts.sort(reverse=True)
        for old_chart in old_charts[5:]:  # Удаляем все кроме последних 5
            try:
                os.remove(os.path.join(static_dir, old_chart))
            except:
                pass
        
        timestamp = int(time.time())
        chart_filename = f'profit_balance_chart_{timestamp}.png'
        chart_path = os.path.join(static_dir, chart_filename)
        
        plt.savefig(chart_path, dpi=300, bbox_inches='tight', facecolor='#1a1a1a')
        plt.close()
        
        # Проверяем, что файл создался
        if os.path.exists(chart_path):
            print(f"График успешно создан: {chart_path}")
        else:
            print(f"Ошибка: файл не создан: {chart_path}")
        
        return f'images/{chart_filename}'
    except Exception as e:
        print(f"Ошибка при создании графиков: {e}")
        return None

def object_detail(request, object_id):
    # Получаем объект или 404
    obj = get_object_or_404(Objekt, id=object_id)
    
    # Получаем ресурсы по объекту, сортируем по категориям с учетом поля order
    resources = ResursyPoObjektu.objects.filter(objekt=obj).select_related('resurs', 'resurs__kategoriya_resursa').order_by('resurs__kategoriya_resursa__order', 'resurs__kategoriya_resursa__nazvanie', 'resurs__naimenovanie')
    
    # Суммарная стоимость ресурсов
    total_cost = sum(float(r.kolichestvo) * float(r.cena) for r in resources)
    
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
    
    # Вычисляем суммы по дням для каждой категории
    category_daily_totals = {}
    for category in set(r.resurs.kategoriya_resursa.nazvanie for r in resources):
        if category != 'Подрядные организации':
            category_daily_totals[category] = {}
            for day in days:
                day_key = day.strftime('%Y-%m-%d')
                daily_total = 0.0
                # Фильтруем ресурсы по категории
                category_resources = [r for r in resources if r.resurs.kategoriya_resursa.nazvanie == category]
                for resource in category_resources:
                    # Ищем фактические ресурсы для этого ресурса
                    for fr in fakticheskij_resursy:
                        if fr.resurs_po_objektu.id == resource.id:
                            # Ищем расходы по дням
                            for rashod in raskhody.get(fr.id, []):
                                if rashod.data.strftime('%Y-%m-%d') == day_key:
                                    # Вычисляем: Заплан.цена * Дневной расход
                                    daily_total += float(resource.cena) * float(rashod.izraskhodovano)
                            break
                category_daily_totals[category][day_key] = daily_total
    
    # Вычисляем итоговые фактические расходы по дням, суммируя значения из итоговых строк категорий
    total_daily_expenses = {}
    for day in days:
        day_key = day.strftime('%Y-%m-%d')
        total_daily_expenses[day_key] = sum(
            category_daily_totals.get(category, {}).get(day_key, 0.0)
            for category in category_daily_totals
        )
    
    from .models import KategoriyaResursa
    from collections import OrderedDict
    categories = KategoriyaResursa.objects.all().order_by('order')
    
    # Группируем ресурсы по категориям
    grouped_resources = OrderedDict()
    for resource in resources:
        category_name = resource.resurs.kategoriya_resursa.nazvanie
        if category_name not in grouped_resources:
            grouped_resources[category_name] = []
        grouped_resources[category_name].append(resource)
    
    context = {
        'object': obj,
        'resources': resources,
        'grouped_resources': grouped_resources,
        'total_cost': total_cost,
        'fakticheskij_resursy': fakticheskij_resursy,
        'raskhody': raskhody,
        'total_spent': total_spent,
        'days': days,
        'category_daily_totals': category_daily_totals,
        'total_daily_expenses': total_daily_expenses,
        'categories': categories,
    }
    
    return render(request, 'object/object_detail.html', context)



def create_object(request):
    from sotrudniki.models import Sotrudnik, Podrazdelenie, Organizaciya
    
    if request.method == 'POST':
        # Обработка создания объекта
        organizaciya_name = request.POST.get('organizaciya')
        nazvanie = request.POST.get('nazvanie')
        data_nachala = request.POST.get('data_nachala')
        
        if nazvanie and data_nachala:
            # Создаем или получаем организацию
            organizaciya = None
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
            
            from datetime import datetime, timedelta
            
            obj = Objekt.objects.create(
                nazvanie=nazvanie,
                organizaciya=organizaciya,
                data_nachala=data_nachala,
                data_plan_zaversheniya=datetime.strptime(data_nachala, '%Y-%m-%d').date() + timedelta(days=365),
                otvetstvennyj="Иванов Иван Иванович"
            )
            
            # Обрабатываем расходные ресурсы
            expense_categories = request.POST.getlist('expense_category[]')
            expense_resources = request.POST.getlist('expense_resource[]')
            expense_quantities = request.POST.getlist('expense_quantity[]')
            expense_prices = request.POST.getlist('expense_price[]')
            
            for i in range(len(expense_resources)):
                if expense_resources[i] and expense_quantities[i] and expense_prices[i]:
                    resurs = Resurs.objects.get(id=expense_resources[i])
                    resurs_po_objektu = ResursyPoObjektu.objects.create(
                        objekt=obj,
                        resurs=resurs,
                        kolichestvo=float(expense_quantities[i]),
                        cena=float(expense_prices[i])
                    )
                    # Создаем фактический ресурс
                    FakticheskijResursPoObjektu.objects.create(
                        resurs_po_objektu=resurs_po_objektu
                    )
            
            # Обрабатываем доходные ресурсы
            income_categories = request.POST.getlist('income_category[]')
            income_resources = request.POST.getlist('income_resource[]')
            income_quantities = request.POST.getlist('income_quantity[]')
            income_prices = request.POST.getlist('income_price[]')
            
            for i in range(len(income_resources)):
                if income_resources[i] and income_quantities[i] and income_prices[i]:
                    resurs = Resurs.objects.get(id=income_resources[i])
                    resurs_po_objektu = ResursyPoObjektu.objects.create(
                        objekt=obj,
                        resurs=resurs,
                        kolichestvo=float(income_quantities[i]),
                        cena=float(income_prices[i])
                    )
                    # Создаем фактический ресурс
                    FakticheskijResursPoObjektu.objects.create(
                        resurs_po_objektu=resurs_po_objektu
                    )
            
            # Создаем начальную запись в сводной таблице
            SvodnayaRaskhodDokhodPoDnyam.objects.create(
                objekt=obj,
                data=datetime.strptime(data_nachala, '%Y-%m-%d').date(),
                raskhod=0,
                dokhod=0,
                balans=0
            )
            
            return redirect('object_detail', object_id=obj.id)
    
    # GET запрос - показываем форму
    sotrudniki = Sotrudnik.objects.select_related('specialnost').all()
    podrazdeleniya = Podrazdelenie.objects.all()
    
    # Получаем категории ресурсов
    from .models import KategoriyaResursa
    expense_categories = KategoriyaResursa.objects.filter(raskhod_dokhod=True)
    income_categories = KategoriyaResursa.objects.filter(raskhod_dokhod=False)
    
    # Получаем следующий ID для значений по умолчанию
    next_id = Objekt.objects.count() + 1
    
    context = {
        'sotrudniki': sotrudniki,
        'podrazdeleniya': podrazdeleniya,
        'expense_categories': list(expense_categories),
        'income_categories': list(income_categories),
        'next_id': next_id,
    }
    
    return render(request, 'object/create_object.html', context)

@csrf_exempt
@require_POST
def add_category(request):
    from .models import KategoriyaResursa
    
    data = json.loads(request.body)
    name = data.get('name')
    
    if name:
        category = KategoriyaResursa.objects.create(nazvanie=name)
        return JsonResponse({'success': True, 'id': category.id})
    
    return JsonResponse({'success': False})

@csrf_exempt
@require_POST
def add_resource(request):
    from .models import Resurs, KategoriyaResursa
    
    data = json.loads(request.body)
    name = data.get('name')
    unit = data.get('unit', 'шт')
    category_id = data.get('category_id')
    
    if name and category_id:
        category = KategoriyaResursa.objects.get(id=category_id)
        resource = Resurs.objects.create(
            naimenovanie=name,
            edinica_izmereniya=unit,
            kategoriya_resursa=category
        )
        return JsonResponse({'success': True, 'id': resource.id})
    
    return JsonResponse({'success': False})

@csrf_exempt
@require_POST
def add_category_to_object(request):
    data = json.loads(request.body)
    category_id = data.get('category_id')
    object_id = data.get('object_id')
    
    if category_id and object_id:
        from .models import KategoriyaResursa, KategoriyaPoObjektu
        
        category = KategoriyaResursa.objects.get(id=category_id)
        obj = Objekt.objects.get(id=object_id)
        
        # Создаем связь между категорией и объектом
        KategoriyaPoObjektu.objects.get_or_create(
            objekt=obj,
            kategoriya=category
        )
        
        return JsonResponse({'success': True})
    
    return JsonResponse({'success': False})

@csrf_exempt
@require_POST
def add_employee_ajax(request):
    from sotrudniki.models import Sotrudnik, Podrazdelenie
    
    data = json.loads(request.body)
    fio = data.get('fio')
    podrazdelenie_id = data.get('podrazdelenie_id')
    
    if fio:
        podrazdelenie = None
        if podrazdelenie_id:
            try:
                podrazdelenie = Podrazdelenie.objects.get(id=podrazdelenie_id)
            except Podrazdelenie.DoesNotExist:
                pass
        
        # Создаем сотрудника с минимальными данными
        from datetime import date
        sotrudnik = Sotrudnik.objects.create(
            fio=fio,
            podrazdelenie=podrazdelenie,
            data_rozhdeniya=date(1990, 1, 1),  # Значение по умолчанию
            data_priema=date.today()
        )
        
        return JsonResponse({'success': True, 'id': sotrudnik.id})
    
    return JsonResponse({'success': False})

def get_resources_by_category(request, category_id):
    from .models import Resurs
    
    resources = Resurs.objects.filter(kategoriya_resursa_id=category_id).values('id', 'naimenovanie', 'edinica_izmereniya')
    return JsonResponse({'resources': list(resources)})

def get_employees_by_resource(request, resource_id):
    from .models import Resurs
    from sotrudniki.models import Sotrudnik, Specialnost
    
    try:
        # Получаем ресурс
        resource = Resurs.objects.get(id=resource_id)
        
        # Ищем специальность по названию ресурса
        try:
            specialnost = Specialnost.objects.get(nazvanie=resource.naimenovanie)
            # Получаем сотрудников с этой специальностью
            employees = Sotrudnik.objects.filter(specialnost=specialnost).values('id', 'fio')
            return JsonResponse({'employees': list(employees)})
        except Specialnost.DoesNotExist:
            return JsonResponse({'employees': []})
            
    except Resurs.DoesNotExist:
        return JsonResponse({'employees': []})

def object_income_detail(request, object_id):
    # Получаем объект или 404
    obj = get_object_or_404(Objekt, id=object_id)
    
    # Получаем только ресурсы категории "Подрядные организации"
    resources = ResursyPoObjektu.objects.filter(
        objekt=obj,
        resurs__kategoriya_resursa__nazvanie='Подрядные организации'
    ).select_related('resurs', 'resurs__kategoriya_resursa')
    
    # Суммарная стоимость ресурсов
    total_cost = sum(float(r.kolichestvo) * float(r.cena) for r in resources)
    
    # Фактические ресурсы
    fakticheskij_resursy = FakticheskijResursPoObjektu.objects.filter(
        resurs_po_objektu__objekt=obj,
        resurs_po_objektu__resurs__kategoriya_resursa__nazvanie='Подрядные организации'
    ).select_related('resurs_po_objektu', 'resurs_po_objektu__resurs')
    
    # Доходы по фактическим ресурсам (из таблицы dokhod_resursa)
    dokhody = {}
    all_dates = set()
    
    for fr in fakticheskij_resursy:
        dokhody_list = DokhodResursa.objects.filter(fakticheskij_resurs=fr).order_by('-data')
        dokhody[fr.id] = dokhody_list
        
        # Собираем все даты доходов
        for dokhod in dokhody_list:
            all_dates.add(dokhod.data)
    
    # Всегда создаем 20 дней для отображения
    today = datetime.now().date()
    days = [today - timedelta(days=i) for i in range(20)]
    
    # Суммарный фактический доход
    total_spent = 0.0
    for fr_id, dd_list in dokhody.items():
        fr = FakticheskijResursPoObjektu.objects.get(id=fr_id)
        resource_cost = float(fr.resurs_po_objektu.cena)
        total_spent += sum(float(dd.vypolneno) * resource_cost for dd in dd_list)
    
    # Вычисляем суммы для строки "Итого"
    # Сумма выполнено по формуле: Σ (Расценка × Σ Дневной доход)
    total_completed = 0.0
    for resource in resources:
        # Ищем фактические ресурсы для этого ресурса
        for fr in fakticheskij_resursy:
            if fr.resurs_po_objektu.id == resource.id:
                # Суммируем все дневные доходы для этого ресурса
                total_daily_income = sum(float(dokhod.vypolneno) for dokhod in dokhody.get(fr.id, []))
                # Вычисляем: Расценка × Σ Дневной доход
                total_completed += float(resource.cena) * total_daily_income
                break
    
    total_remaining = sum(float(r.kolichestvo - r.potracheno) for r in resources)  # Сумма осталось
    
    # Вычисляем суммы по дням для подрядных организаций (из таблицы dokhod_resursa)
    daily_totals = {}
    for day in days:
        day_key = day.strftime('%Y-%m-%d')
        daily_total = 0.0
        for resource in resources:
            # Ищем фактические ресурсы для этого ресурса
            for fr in fakticheskij_resursy:
                if fr.resurs_po_objektu.id == resource.id:
                    # Ищем доходы по дням
                    for dokhod in dokhody.get(fr.id, []):
                        if dokhod.data.strftime('%Y-%m-%d') == day_key:
                            # Вычисляем: Расценка * Дневной доход
                            daily_total += float(resource.cena) * float(dokhod.vypolneno)
                    break
        daily_totals[day_key] = daily_total
    
    context = {
        'object': obj,
        'resources': resources,
        'total_cost': total_cost,
        'fakticheskij_resursy': fakticheskij_resursy,
        'dokhody': dokhody,
        'total_spent': total_spent,
        'days': days,
        'is_income_page': True,  # Флаг для шаблона
        'total_completed': total_completed,  # Сумма выполнено
        'total_remaining': total_remaining,  # Сумма осталось
        'daily_totals': daily_totals,
    }
    
    return render(request, 'object/object_income_detail.html', context)

@csrf_exempt
@require_POST
def update_expense(request):
    max_retries = 3
    retry_delay = 0.1  # 100ms
    
    for attempt in range(max_retries):
        try:
            data = json.loads(request.body)
            resource_id = data.get('resource_id')
            date_str = data.get('date')
            amount = data.get('amount', 0)
            
            # Преобразуем в Decimal для совместимости с моделью
            from decimal import Decimal
            amount = Decimal(str(amount))
            
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
            ).aggregate(total=Sum('izraskhodovano'))['total'] or Decimal('0')
            
            # Обновляем поле potracheno в resursy_po_objektu
            resource.potracheno = total_spent
            resource.save()
            
            return JsonResponse({
                'success': True,
                'potracheno': float(total_spent),
                'ostatok': float(resource.kolichestvo - total_spent)
            })
            
        except Exception as e:
            error_msg = str(e)
            if 'database is locked' in error_msg.lower() and attempt < max_retries - 1:
                # Если база заблокирована и это не последняя попытка, ждем и повторяем
                time.sleep(retry_delay)
                retry_delay *= 2  # Увеличиваем задержку с каждой попыткой
                continue
            else:
                # Если это последняя попытка или другая ошибка, возвращаем ошибку
                return JsonResponse({'success': False, 'error': error_msg})
    
    # Если все попытки исчерпаны
    return JsonResponse({'success': False, 'error': 'Database is locked after multiple attempts'})

@csrf_exempt
@require_POST
def update_resource_data(request):
    max_retries = 3
    retry_delay = 0.1  # 100ms
    
    for attempt in range(max_retries):
        try:
            data = json.loads(request.body)
            resource_id = data.get('resource_id')
            field_type = data.get('field_type')  # 'kolichestvo' или 'cena'
            new_value = data.get('value', 0)
            
            # Преобразуем в Decimal для совместимости с моделью
            from decimal import Decimal
            new_value = Decimal(str(new_value))
            
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
            error_msg = str(e)
            if 'database is locked' in error_msg.lower() and attempt < max_retries - 1:
                # Если база заблокирована и это не последняя попытка, ждем и повторяем
                time.sleep(retry_delay)
                retry_delay *= 2  # Увеличиваем задержку с каждой попыткой
                continue
            else:
                # Если это последняя попытка или другая ошибка, возвращаем ошибку
                return JsonResponse({'success': False, 'error': error_msg})
    
    # Если все попытки исчерпаны
    return JsonResponse({'success': False, 'error': 'Database is locked after multiple attempts'})

@csrf_exempt
@require_POST
def delete_object(request, object_id):
    try:
        obj = get_object_or_404(Objekt, id=object_id)
        obj.is_active = False
        obj.save()
        return JsonResponse({'success': True})
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)})

@csrf_exempt
@require_POST
def add_resource_to_object(request):
    try:
        data = json.loads(request.body)
        object_id = data.get('object_id')
        resource_id = data.get('resource_id')
        quantity = data.get('quantity')
        price = data.get('price')
        
        if not all([object_id, resource_id, quantity, price]):
            return JsonResponse({'success': False, 'error': 'Не все поля заполнены'})
        
        obj = get_object_or_404(Objekt, id=object_id)
        resurs = get_object_or_404(Resurs, id=resource_id)
        
        # Создаем ресурс по объекту
        resurs_po_objektu = ResursyPoObjektu.objects.create(
            objekt=obj,
            resurs=resurs,
            kolichestvo=quantity,
            cena=price
        )
        
        # Создаем фактический ресурс
        FakticheskijResursPoObjektu.objects.create(
            resurs_po_objektu=resurs_po_objektu
        )
        
        return JsonResponse({'success': True})
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)})

@csrf_exempt
@require_POST
def delete_resource_from_object(request):
    try:
        data = json.loads(request.body)
        resource_id = data.get('resource_id')
        
        if not resource_id:
            return JsonResponse({'success': False, 'error': 'Не указан ID ресурса'})
        
        resurs_po_objektu = get_object_or_404(ResursyPoObjektu, id=resource_id)
        FakticheskijResursPoObjektu.objects.filter(resurs_po_objektu=resurs_po_objektu).delete()
        resurs_po_objektu.delete()
        
        return JsonResponse({'success': True})
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)})