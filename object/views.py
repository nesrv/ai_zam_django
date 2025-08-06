from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth import login
from django.contrib.auth.models import User
from django.db.models import Sum, Count, F
from .models import Objekt, ResursyPoObjektu, RaskhodResursa, Resurs, FakticheskijResursPoObjektu, DokhodResursa, SvodnayaRaskhodDokhodPoDnyam, UserProfile
from .forms import UserRegistrationForm, OrganizationForm, UserProfileForm, UserPhotoForm
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
from sotrudniki.models import Sotrudnik, Specialnost, Organizaciya

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
    
    # Фильтруем объекты для авторизованного пользователя
    if request.user.is_authenticated:
        user_profile, created = UserProfile.objects.get_or_create(user=request.user)
        organizations = user_profile.organizations.all()
        from django.db.models import Q
        objects = Objekt.objects.filter(
            Q(organizacii__in=organizations) | Q(otvetstvennyj__icontains=request.user.get_full_name()),
            is_active=True
        ).distinct()
    else:
        objects = Objekt.objects.filter(demo=True, is_active=True)
    
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
    
    # Получаем только расходные ресурсы (raskhod_dokhod=True)
    resources = ResursyPoObjektu.objects.filter(
        objekt=obj,
        resurs__kategoriya_resursa__raskhod_dokhod=True
    ).select_related('resurs', 'resurs__kategoriya_resursa').order_by('resurs__kategoriya_resursa__order', 'resurs__kategoriya_resursa__nazvanie', 'resurs__naimenovanie')
    
    # Суммарная стоимость ресурсов
    total_cost = sum(float(r.kolichestvo) * float(r.cena) for r in resources)
    
    # Фактические расходные ресурсы
    fakticheskij_resursy = FakticheskijResursPoObjektu.objects.filter(
        resurs_po_objektu__objekt=obj,
        resurs_po_objektu__resurs__kategoriya_resursa__raskhod_dokhod=True
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
    
    # Вычисляем суммы по дням для каждой расходной категории
    category_daily_totals = {}
    for category in set(r.resurs.kategoriya_resursa.nazvanie for r in resources):
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
                data_nachala=data_nachala,
                data_plan_zaversheniya=datetime.strptime(data_nachala, '%Y-%m-%d').date() + timedelta(days=365),
                otvetstvennyj="Иванов Иван Иванович",
                demo=not request.user.is_authenticated
            )
            
            # Добавляем организацию через ManyToMany
            if organizaciya:
                obj.organizacii.add(organizaciya)
            
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
    
    # Получаем организации пользователя
    user_organizations = []
    if request.user.is_authenticated:
        user_profile, created = UserProfile.objects.get_or_create(user=request.user)
        user_organizations = user_profile.organizations.all()
    else:
        # Для неавторизованных пользователей показываем демо-организации
        user_organizations = Organizaciya.objects.filter(demo=True)
    
    # Получаем следующий ID для значений по умолчанию
    next_id = Objekt.objects.count() + 1
    
    context = {
        'sotrudniki': sotrudniki,
        'podrazdeleniya': podrazdeleniya,
        'expense_categories': list(expense_categories),
        'income_categories': list(income_categories),
        'user_organizations': user_organizations,
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

@csrf_exempt
def check_employee_in_object(request, object_id, employee_id):
    """API endpoint для проверки наличия сотрудника на объекте"""
    try:
        obj = get_object_or_404(Objekt, id=object_id)
        from sotrudniki.models import Sotrudnik
        employee = get_object_or_404(Sotrudnik, id=employee_id)
        
        is_assigned = obj.sotrudniki.filter(id=employee_id).exists()
        
        return JsonResponse({
            'success': True, 
            'is_assigned': is_assigned,
            'employee': {
                'id': employee.id,
                'fio': employee.fio,
                'specialnost': employee.specialnost.nazvanie if employee.specialnost else None
            }
        })
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)})

@csrf_exempt
def add_employee_to_object_api(request, object_id, employee_id):
    """API endpoint для добавления сотрудника на объект"""
    try:
        obj = get_object_or_404(Objekt, id=object_id)
        from sotrudniki.models import Sotrudnik
        employee = get_object_or_404(Sotrudnik, id=employee_id)
        
        # Проверяем, есть ли уже сотрудник на объекте
        if not obj.sotrudniki.filter(id=employee_id).exists():
            obj.sotrudniki.add(employee)
            action = 'added'
        else:
            # Если сотрудник уже на объекте, удаляем его
            obj.sotrudniki.remove(employee)
            action = 'removed'
        
        return JsonResponse({
            'success': True, 
            'action': action,
            'employee': {
                'id': employee.id,
                'fio': employee.fio,
                'specialnost': employee.specialnost.nazvanie if employee.specialnost else None
            }
        })
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)})

@csrf_exempt
def get_employees_by_position(request, object_id):
    """API для получения сотрудников по должности"""
    try:
        position = request.GET.get('position', '')
        print(f"\nПолучен запрос на сотрудников по позиции: {position}")
        
        # Получаем объект
        obj = get_object_or_404(Objekt, id=object_id)
        
        # Находим специальности, подходящие по названию
        specialnosti = Specialnost.objects.filter(nazvanie__icontains=position)
        
        # Если не нашли специальность, ищем по части слова
        if not specialnosti.exists() and position:
            words = position.split()
            for word in words:
                if len(word) > 3:  # Ищем только по словам длиннее 3 символов
                    specialnosti = specialnosti | Specialnost.objects.filter(nazvanie__icontains=word)
        
        # Получаем всех сотрудников
        employees = Sotrudnik.objects.all()
        
        # Фильтруем по специальностям, если они найдены
        if specialnosti.exists():
            filtered_employees = []
            for spec in specialnosti:
                filtered_employees.extend(employees.filter(specialnost=spec))
            employees = filtered_employees
        
        # Ограничиваем количество сотрудников
        if not employees:
            employees = Sotrudnik.objects.all()[:5]
        
        # Формируем список сотрудников
        employees_data = []
        for employee in employees:
            employees_data.append({
                'id': employee.id,
                'fio': employee.fio,
                'organizaciya': employee.organizaciya.nazvanie if employee.organizaciya else None,
                'podrazdelenie': employee.podrazdelenie.nazvanie if employee.podrazdelenie else None,
                'specialnost': employee.specialnost.nazvanie if employee.specialnost else None,
            })
        
        return JsonResponse({'success': True, 'employees': employees_data})
    except Exception as e:
        print(f"Ошибка при получении сотрудников: {str(e)}")
        return JsonResponse({'success': False, 'error': str(e)})

def object_income_detail(request, object_id):
    # Получаем объект или 404
    obj = get_object_or_404(Objekt, id=object_id)
    
    # Получаем только ресурсы с raskhod_dokhod=0 (False)
    resources = ResursyPoObjektu.objects.filter(
        objekt=obj,
        resurs__kategoriya_resursa__raskhod_dokhod=0
    ).select_related('resurs', 'resurs__kategoriya_resursa').order_by('resurs__kategoriya_resursa__order', 'resurs__kategoriya_resursa__nazvanie', 'resurs__naimenovanie')
    
    # Суммарная стоимость ресурсов
    total_cost = sum(float(r.kolichestvo) * float(r.cena) for r in resources)
    
    # Фактические ресурсы с raskhod_dokhod=0
    fakticheskij_resursy = FakticheskijResursPoObjektu.objects.filter(
        resurs_po_objektu__objekt=obj,
        resurs_po_objektu__resurs__kategoriya_resursa__raskhod_dokhod=0
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
    
    # Вычисляем суммы по дням для каждой категории с raskhod_dokhod=0
    category_daily_totals = {}
    for category in set(r.resurs.kategoriya_resursa.nazvanie for r in resources):
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
    
    # Вычисляем итоговые фактические расходы по дням
    total_daily_expenses = {}
    for day in days:
        day_key = day.strftime('%Y-%m-%d')
        total_daily_expenses[day_key] = sum(
            category_daily_totals.get(category, {}).get(day_key, 0.0)
            for category in category_daily_totals
        )
    
    from .models import KategoriyaResursa
    from collections import OrderedDict
    categories = KategoriyaResursa.objects.filter(raskhod_dokhod=0).order_by('order')
    
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
            elif field_type == 'both':
                quantity = data.get('quantity', 0)
                price = data.get('price', 0)
                resource.kolichestvo = Decimal(str(quantity))
                resource.cena = Decimal(str(price))
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

@csrf_exempt
def get_employees_by_object_position(request, object_id):
    """API endpoint для получения сотрудников по объекту и должности"""
    try:
        position = request.GET.get('position')
        
        if not position:
            return JsonResponse({'success': False, 'error': 'Не указана должность'})
        
        # Получаем объект
        obj = get_object_or_404(Objekt, id=object_id)
        
        # Отладочная информация
        print(f"\nПоиск сотрудников для объекта ID: {object_id}, должность: {position}")
        
        # Получаем всех сотрудников, привязанных к объекту
        all_employees = obj.sotrudniki.all()
        print(f"Всего сотрудников на объекте: {all_employees.count()}")
        
        # Если нет сотрудников на объекте, возвращаем всех сотрудников с подходящей специальностью
        if all_employees.count() == 0:
            print("Нет сотрудников на объекте, ищем по специальности")
            from sotrudniki.models import Sotrudnik
            all_employees = Sotrudnik.objects.all()
        
        # Находим специальности, подходящие по названию
        specialnosti = Specialnost.objects.filter(nazvanie__icontains=position)
        print(f"Найдено специальностей по запросу '{position}': {specialnosti.count()}")
        
        # Если не нашли специальность, пробуем поиск по части слова
        if specialnosti.count() == 0:
            # Разбиваем название должности на слова и ищем по каждому слову
            words = position.split()
            for word in words:
                if len(word) > 3:  # Ищем только по словам длиннее 3 символов
                    word_specialnosti = Specialnost.objects.filter(nazvanie__icontains=word)
                    print(f"Поиск по слову '{word}': найдено {word_specialnosti.count()}")
                    specialnosti = specialnosti | word_specialnosti
        
        # Фильтруем сотрудников по найденным специальностям
        employees = []
        if specialnosti.count() > 0:
            for spec in specialnosti:
                spec_employees = all_employees.filter(specialnost=spec)
                print(f"Специальность '{spec.nazvanie}': найдено сотрудников {spec_employees.count()}")
                employees.extend(spec_employees)
        else:
            # Если не нашли подходящих специальностей, возвращаем всех сотрудников на объекте
            employees = list(all_employees)
            print(f"Специальности не найдены, возвращаем всех сотрудников: {len(employees)}")
        
        # Удаляем дубликаты
        unique_employees = []
        employee_ids = set()
        for emp in employees:
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
        
        print(f"Итого найдено уникальных сотрудников: {len(employees_data)}")
        return JsonResponse({'success': True, 'employees': employees_data})
    except Exception as e:
        print(f"Ошибка при поиске сотрудников: {str(e)}")
        return JsonResponse({'success': False, 'error': str(e)})


@csrf_exempt
def check_employee_in_object(request, object_id, employee_id):
    """API endpoint для проверки, привязан ли сотрудник к объекту"""
    try:
        # Получаем объект
        obj = get_object_or_404(Objekt, id=object_id)
        
        # Проверяем, есть ли сотрудник в списке сотрудников объекта
        is_added = obj.sotrudniki.filter(id=employee_id).exists()
        
        return JsonResponse({
            'success': True, 
            'is_added': is_added,
            'object_id': object_id,
            'employee_id': employee_id
        })
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)})


@csrf_exempt
@require_POST
def save_employee_hours(request, object_id):
    """API endpoint для сохранения отработанных часов сотрудников в таблицу sotrudniki_zarplaty"""
    try:
        # Получаем объект
        obj = get_object_or_404(Objekt, id=object_id)
        
        # Получаем данные из запроса
        data = json.loads(request.body)
        position = data.get('position', '')
        date_str = data.get('date', '')
        employees = data.get('employees', [])
        total_hours = data.get('total_hours', 0)
        
        # Преобразуем строку даты в объект date
        from datetime import datetime
        try:
            date_obj = datetime.strptime(date_str, '%Y-%m-%d').date()
        except ValueError:
            return JsonResponse({'success': False, 'error': 'Неверный формат даты'})
        
        # Импортируем модель SotrudnikiZarplaty
        from sotrudniki.models import Sotrudnik, SotrudnikiZarplaty
        
        # Сохраняем данные для каждого сотрудника
        saved_count = 0
        for emp_data in employees:
            employee_id = emp_data.get('employee_id')
            fio = emp_data.get('fio', '')
            hours = emp_data.get('hours', 0)
            kpi = emp_data.get('kpi', 1.0)
            
            # Если employee_id не указан, пытаемся найти сотрудника по ФИО
            if not employee_id:
                try:
                    employee = Sotrudnik.objects.filter(fio__icontains=fio).first()
                    if employee:
                        employee_id = employee.id
                except:
                    pass
            
            # Создаем или обновляем запись в таблице SotrudnikiZarplaty
            if employee_id:
                try:
                    # Пытаемся найти существующую запись
                    zarplata, created = SotrudnikiZarplaty.objects.update_or_create(
                        sotrudnik_id=employee_id,
                        objekt=obj,
                        data=date_obj,
                        defaults={
                            'kolichestvo_chasov': hours,
                            'kpi': kpi
                        }
                    )
                    saved_count += 1
                except Exception as e:
                    print(f"Ошибка при сохранении данных для сотрудника {fio}: {str(e)}")
        
        # Сохраняем данные в таблицу raskhod_resursa
        try:
            # Находим ресурс по объекту с указанной должностью
            from .models import ResursyPoObjektu, FakticheskijResursPoObjektu, RaskhodResursa, Resurs
            
            # Находим ресурс с указанной должностью
            resource = ResursyPoObjektu.objects.filter(
                objekt=obj,
                resurs__naimenovanie__icontains=position
            ).first()
            
            if not resource:
                # Если не нашли по точному совпадению, ищем по частичному
                resources = ResursyPoObjektu.objects.filter(
                    objekt=obj,
                    resurs__kategoriya_resursa__nazvanie__icontains="Кадровое"
                )
                
                for res in resources:
                    if position.lower() in res.resurs.naimenovanie.lower() or res.resurs.naimenovanie.lower() in position.lower():
                        resource = res
                        break
            
            if resource:
                # Получаем или создаем фактический ресурс
                fakticheskij_resurs, created = FakticheskijResursPoObjektu.objects.get_or_create(
                    resurs_po_objektu=resource
                )
                
                # Создаем или обновляем запись в таблице RaskhodResursa
                raskhod, created = RaskhodResursa.objects.update_or_create(
                    fakticheskij_resurs=fakticheskij_resurs,
                    data=date_obj,
                    defaults={
                        'izraskhodovano': total_hours
                    }
                )
                
                # Обновляем поле potracheno в ресурсе
                from django.db.models import Sum
                total_spent = RaskhodResursa.objects.filter(
                    fakticheskij_resurs=fakticheskij_resurs
                ).aggregate(total=Sum('izraskhodovano'))['total'] or 0
                
                resource.potracheno = total_spent
                resource.save()
                
                print(f"Успешно сохранено в таблицу raskhod_resursa: {total_hours} часов для {position} на дату {date_obj}")
            else:
                print(f"Не найден ресурс для должности {position}")
        except Exception as e:
            print(f"Ошибка при сохранении в таблицу raskhod_resursa: {str(e)}")
        
        # Обновляем ячейку в основной таблице
        
        return JsonResponse({
            'success': True, 
            'message': f'Сохранено записей: {saved_count}',
            'saved_count': saved_count,
            'total_hours': total_hours
        })
    except Exception as e:
        print(f"Ошибка при сохранении часов: {str(e)}")
        return JsonResponse({'success': False, 'error': str(e)})


def debug_employees(request, object_id):
    """Отладочный эндпоинт для вывода информации при клике на 👥"""
    try:
        # Получаем параметры из запроса
        position = request.GET.get('position', '')
        date = request.GET.get('date', '')
        
        # Выводим отладочную информацию в терминал
        print(f"\n\n*** DEBUG EMPLOYEE CLICK ***")
        print(f"Object ID: {object_id}")
        print(f"Position: {position}")
        print(f"Date: {date}")
        print("*************************\n\n")
        
        # Возвращаем успешный ответ
        return JsonResponse({
            'success': True,
            'debug': {
                'object_id': object_id,
                'position': position,
                'date': date
            }
        })
    except Exception as e:
        print(f"Error in debug_employees: {str(e)}")
        return JsonResponse({'success': False, 'error': str(e)})


def get_salary_data(request, object_id):
    """Получение данных из таблицы sotrudniki_zarplaty для отображения в модальном окне"""
    try:
        from sotrudniki.models import SotrudnikiZarplaty, Sotrudnik
        from datetime import datetime
        from django.db.models import Sum
        
        # Получаем параметры из запроса
        position = request.GET.get('position', '')
        date_str = request.GET.get('date', '')
        
        # Преобразуем дату из формата DD.MM в YYYY-MM-DD
        date_obj = None
        if date_str and date_str.strip():
            try:
                # Проверяем разные форматы даты
                if '.' in date_str:
                    # Формат DD.MM
                    day, month = date_str.split('.')
                    year = datetime.now().year
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
        from object.models import Objekt
        objekt = get_object_or_404(Objekt, id=object_id)
        
        # Получаем сотрудников по должности
        from sotrudniki.models import Sotrudnik, Specialnost
        
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
            from object.models import ResursyPoObjektu, FakticheskijResursPoObjektu, RaskhodResursa
            
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
        if employees_data:
            # Получаем сумму часов из записей сотрудников
            sum_hours = sum(emp['hours'] for emp in employees_data)
            
            # Если сумма часов не соответствует общему количеству часов в ячейке,
            # корректируем часы для каждого сотрудника
            if total_hours > 0 and abs(sum_hours - total_hours) > 0.01:
                # Если есть только один сотрудник, просто устанавливаем ему все часы
                if len(employees_data) == 1:
                    employees_data[0]['hours'] = total_hours
                # Если сотрудников несколько, распределяем часы пропорционально
                elif len(employees_data) > 1 and sum_hours > 0:
                    ratio = total_hours / sum_hours
                    for emp in employees_data:
                        emp['hours'] = round(emp['hours'] * ratio, 2)
        
        return JsonResponse({
            'success': True,
            'employees': employees_data,
            'position': position,
            'date': date_str,
            'total_hours': total_hours  # Добавляем общее количество часов для отладки
        })
    except Exception as e:
        print(f"Ошибка получения данных о зарплате: {str(e)}")
        return JsonResponse({'success': False, 'error': str(e)})


@csrf_exempt
@require_POST
def add_employee_to_object_api(request, object_id, employee_id):
    """API endpoint для добавления сотрудника к объекту"""
    try:
        # Получаем объект и сотрудника
        obj = get_object_or_404(Objekt, id=object_id)
        from sotrudniki.models import Sotrudnik
        employee = get_object_or_404(Sotrudnik, id=employee_id)
        
        # Добавляем сотрудника к объекту
        obj.sotrudniki.add(employee)
        
        # Проверяем, что сотрудник действительно добавлен
        is_added = obj.sotrudniki.filter(id=employee_id).exists()
        
        if is_added:
            return JsonResponse({
                'success': True, 
                'message': f'Сотрудник {employee.fio} успешно добавлен к объекту {obj.nazvanie}'
            })
        else:
            # Если сотрудник не добавлен, пробуем еще раз другим способом
            try:
                # Альтернативный способ добавления через SQL
                from django.db import connection
                with connection.cursor() as cursor:
                    cursor.execute(
                        "INSERT INTO objekt_sotrudniki (objekt_id, sotrudnik_id) VALUES (%s, %s)",
                        [object_id, employee_id]
                    )
                return JsonResponse({
                    'success': True, 
                    'message': f'Сотрудник {employee.fio} добавлен к объекту {obj.nazvanie} (альтернативный метод)'
                })
            except Exception as e2:
                return JsonResponse({
                    'success': False, 
                    'error': f'Не удалось добавить сотрудника (альтернативный метод): {str(e2)}'
                })
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)})
def register(request):
    if request.method == 'POST':
        form = UserRegistrationForm(request.POST)
        photo_form = UserPhotoForm(request.POST, request.FILES)
        if form.is_valid() and photo_form.is_valid():
            # Создаем пользователя
            user = User.objects.create_user(
                username=form.cleaned_data['username'],
                first_name=form.cleaned_data['first_name'],
                last_name=form.cleaned_data['last_name'],
                password=form.cleaned_data['password']
            )
            
            # Создаем профиль
            profile = UserProfile.objects.create(user=user)
            if photo_form.cleaned_data['photo']:
                profile.photo = photo_form.cleaned_data['photo']
                profile.save()
            
            # Авторизуем пользователя
            login(request, user)
            
            return redirect('/objects/profile/')
    else:
        form = UserRegistrationForm()
        photo_form = UserPhotoForm()
    return render(request, 'object/register.html', {'form': form, 'photo_form': photo_form})
def profile(request):
    if not request.user.is_authenticated:
        # Создаем временный профиль для неавторизованного пользователя
        from django.contrib.auth.models import AnonymousUser
        user_profile = type('TempProfile', (), {
            'organizations': type('TempManager', (), {
                'all': lambda: Organizaciya.objects.filter(demo=True),
                'add': lambda org: None
            })(),
            'photo': type('Photo', (), {
                'url': '/media/user_photos/avatar_default.jpg'
            })()
        })()
    else:
        # Получаем или создаем профиль пользователя
        user_profile, created = UserProfile.objects.get_or_create(user=request.user)
        # Если у пользователя нет фото, устанавливаем фото по умолчанию
        if not user_profile.photo:
            user_profile.photo = type('Photo', (), {
                'url': '/media/user_photos/avatar_default.jpg'
            })()
    

    
    # Инициализируем формы
    if request.user.is_authenticated:
        user_form = UserProfileForm(instance=request.user)
        photo_form = UserPhotoForm(instance=user_profile)
    else:
        user_form = None
        photo_form = None
    org_form = OrganizationForm()
    
    if request.method == 'POST':
        if 'add_bot' in request.POST:
            bot_name = request.POST.get('bot_name')
            bot_token = request.POST.get('bot_token')
            if bot_name and bot_token:
                from telegrambot.models import Bot
                Bot.objects.create(
                    user=request.user,
                    bot_name=bot_name,
                    token=bot_token
                )
                return redirect('/objects/profile/?success=1')
        elif 'add_organization' in request.POST:
            org_form = OrganizationForm(request.POST)
            if org_form.is_valid():
                from sotrudniki.models import Organizaciya, OrganizaciyaPodrazdelenie
                org_data = org_form.cleaned_data
                org_data['demo'] = not request.user.is_authenticated
                org = Organizaciya.objects.create(**org_data)
                # Для авторизованных пользователей добавляем организацию к профилю
                if request.user.is_authenticated:
                    user_profile.organizations.add(org)
                # Добавляем подразделение "Линейные сотрудники" для новой организации
                OrganizaciyaPodrazdelenie.objects.create(organizaciya=org, podrazdelenie_id=3)
                return redirect('/objects/profile/?success=1')
        elif 'remove_organization' in request.POST:
            org_id = request.POST.get('remove_organization')
            if org_id and request.user.is_authenticated:
                from sotrudniki.models import Organizaciya
                try:
                    org = Organizaciya.objects.get(id=org_id)
                    user_profile.organizations.remove(org)
                except Organizaciya.DoesNotExist:
                    pass
                return redirect('/objects/profile/?success=1')
        elif 'remove_bot_name' in request.POST:
            bot_name = request.POST.get('remove_bot_name')
            bot_token = request.POST.get('remove_bot_token')
            if bot_name and bot_token:
                from telegrambot.models import Bot
                Bot.objects.filter(user=request.user, bot_name=bot_name, token=bot_token).delete()
                return redirect('/objects/profile/?success=1')
        elif 'add_camera' in request.POST:
            name = request.POST.get('camera_name')
            url = request.POST.get('camera_url')
            objekt_id = request.POST.get('camera_objekt')
            location = request.POST.get('camera_location', '')
            description = request.POST.get('camera_description', '')
            if name and url and objekt_id:
                from cams.models import Camera
                Camera.objects.create(
                    name=name,
                    url=url,
                    objekt_id=objekt_id,
                    location=location,
                    description=description
                )
                return redirect('/objects/profile/?success=1')
        elif 'remove_camera' in request.POST:
            camera_id = request.POST.get('remove_camera')
            if camera_id:
                from cams.models import Camera
                try:
                    camera = Camera.objects.get(id=camera_id)
                    camera.delete()
                except Camera.DoesNotExist:
                    pass
                return redirect('/objects/profile/?success=1')
        else:
            if request.user.is_authenticated:
                user_form = UserProfileForm(request.POST, instance=request.user)
                photo_form = UserPhotoForm(request.POST, request.FILES, instance=user_profile)
                
                if user_form.is_valid() and photo_form.is_valid():
                    user_form.save()
                    photo_form.save()
            return redirect('/objects/profile/?success=1')
    
    # Получаем организации пользователя
    organizations = user_profile.organizations.all()
    
    # Получаем ботов пользователя (агрегированные по названию и токену)
    from telegrambot.models import Bot
    bots = Bot.objects.filter(user=request.user).values('bot_name', 'token').distinct()
    
    # Получаем камеры пользователя
    from cams.models import Camera
    cameras = Camera.objects.filter(objekt__organizacii__in=organizations).distinct()
    
    # Получаем объекты связанные с организациями пользователя (только если есть организации)
    if organizations.exists():
        from django.db.models import Q
        objects = Objekt.objects.filter(
            Q(organizacii__in=organizations) | Q(otvetstvennyj__icontains=request.user.get_full_name())
        ).distinct()
    else:
        objects = Objekt.objects.none()
    
    # Получаем рабочие чаты (объекты с chat_id)
    work_chats = objects.filter(chat_id__isnull=False).values('id', 'nazvanie', 'chat_id')
    
    # Группируем объекты по организациям
    objects_by_organization = {}
    for org in organizations:
        org_objects = objects.filter(organizacii=org)
        if org_objects.exists():
            objects_by_organization[org] = org_objects
    
    # Объекты без организации (только по ответственному)
    objects_without_org = objects.filter(otvetstvennyj__icontains=request.user.get_full_name()).exclude(organizacii__in=organizations)
    
    context = {
        'profile': user_profile,
        'user_form': user_form,
        'photo_form': photo_form,
        'org_form': org_form,
        'organizations': organizations,
        'objects_by_organization': objects_by_organization,
        'objects_without_org': objects_without_org,
        'bots': bots,
        'cameras': cameras,
        'work_chats': work_chats,
    }
    
    return render(request, 'object/profile.html', context)
def demo_profile(request):
    from sotrudniki.models import Organizaciya
    
    # Получаем демо-организации
    organizations = Organizaciya.objects.filter(demo=True)
    
    # Получаем демо-объекты
    demo_objects = Objekt.objects.filter(demo=True)
    
    # Создаем временный профиль с фото по умолчанию
    demo_profile = type('DemoProfile', (), {
        'photo': type('Photo', (), {
            'url': '/media/user_photos/avatar_default.jpg'
        })()
    })()
    
    # Группируем объекты по организациям для демо-режима
    objects_by_organization = {}
    for org in organizations:
        org_objects = demo_objects.filter(organizacii=org)
        if org_objects.exists():
            objects_by_organization[org] = org_objects
    
    # Объекты без организации
    objects_without_org = demo_objects.filter(organizacii__isnull=True)
    
    # Создаем демо-ботов
    demo_bots = [
        {'bot_name': 'Демо-бот 1', 'token': 'demo_token_123456789'},
        {'bot_name': 'Демо-бот 2', 'token': 'demo_token_987654321'}
    ]
    
    context = {
        'organizations': organizations,
        'objects': demo_objects,
        'objects_by_organization': objects_by_organization,
        'objects_without_org': objects_without_org,
        'is_demo': True,
        'profile': demo_profile,
        'bots': demo_bots,
        'user': type('DemoUser', (), {
            'get_full_name': lambda: 'Демо пользователь',
            'username': 'demo',
            'date_joined': '01.01.2024'
        })()
    }
    
    return render(request, 'object/profile.html', context)

def logout_view(request):
    from django.contrib.auth import logout
    logout(request)
    return redirect('home')
def login_view(request):
    if request.method == 'POST':
        from django.contrib.auth import authenticate, login
        username = request.POST.get('username')
        password = request.POST.get('password')
        
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('/objects/profile/')
        else:
            return render(request, 'object/login.html', {'error': 'Неверный логин или пароль'})
    
    return render(request, 'object/login.html')

@csrf_exempt
@require_POST
def add_chat_to_object(request, object_id):
    try:
        data = json.loads(request.body)
        chat_id = data.get('chat_id')
        
        obj = get_object_or_404(Objekt, id=object_id)
        
        if chat_id == '' or chat_id is None:
            obj.chat_id = None
        else:
            obj.chat_id = chat_id
        
        obj.save()
        
        return JsonResponse({'success': True})
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)})

def add_bot(request):
    if not request.user.is_authenticated:
        return redirect('/objects/login/')
    
    if request.method == 'POST':
        bot_name = request.POST.get('bot_name')
        new_bot_name = request.POST.get('new_bot_name')
        bot_token = request.POST.get('bot_token')
        
        # Используем новое имя, если выбрано "Создать нового бота"
        final_bot_name = new_bot_name if bot_name == 'new' else bot_name
        
        if final_bot_name and bot_token:
            from telegrambot.models import Bot
            Bot.objects.create(
                user=request.user,
                bot_name=final_bot_name,
                token=bot_token
            )
            return redirect('/objects/profile/')
    
    # Получаем ботов пользователя
    from telegrambot.models import Bot
    user_bots = Bot.objects.filter(user=request.user)
    
    return render(request, 'object/add_bot.html', {'user_bots': user_bots})

@csrf_exempt
@require_POST
def get_chat_ids(request):
    try:
        import requests
        data = json.loads(request.body)
        bot_token = data.get('bot_token')
        
        if not bot_token:
            return JsonResponse({'success': False, 'error': 'Токен не указан'})
        
        url = f'https://api.telegram.org/bot{bot_token}/getUpdates'
        response = requests.get(url)
        
        if response.status_code != 200:
            return JsonResponse({'success': False, 'error': 'Ошибка API Telegram'})
        
        result = response.json()
        
        if not result.get('ok'):
            return JsonResponse({'success': False, 'error': result.get('description', 'Неизвестная ошибка')})
        
        chat_ids = set()
        for update in result.get('result', []):
            if 'message' in update:
                chat_id = update['message']['chat']['id']
                chat_title = update['message']['chat'].get('title', 'Личный чат')
                chat_type = update['message']['chat']['type']
                
                if chat_type in ['group', 'supergroup']:
                    chat_ids.add((chat_id, chat_title))
        
        if not chat_ids:
            return JsonResponse({
                'success': False, 
                'error': 'Нет сообщений от групп. Отправьте любое сообщение боту в группе, затем повторите попытку.'
            })
        
        for chat_id, chat_title in chat_ids:
            send_url = f'https://api.telegram.org/bot{bot_token}/sendMessage'
            send_data = {
                'chat_id': chat_id,
                'text': 'Бот подключен к рабочей группе'
            }
            requests.post(send_url, json=send_data)
        
        user_profile, created = UserProfile.objects.get_or_create(user=request.user)
        organizations = user_profile.organizations.all()
        
        from django.db.models import Q
        objects = Objekt.objects.filter(
            Q(organizacii__in=organizations) | Q(otvetstvennyj__icontains=request.user.get_full_name())
        ).distinct()
        
        updated_objects = []
        chat_list = list(chat_ids)
        
        for i, obj in enumerate(objects.filter(chat_id__isnull=True)):
            if i < len(chat_list):
                obj.chat_id = chat_list[i][0]
                obj.save()
                updated_objects.append({
                    'object_name': obj.nazvanie,
                    'chat_id': chat_list[i][0],
                    'chat_title': chat_list[i][1]
                })
        
        return JsonResponse({
            'success': True,
            'chat_ids': [{'id': cid, 'title': title} for cid, title in chat_ids],
            'updated_objects': updated_objects
        })
        
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)})
@csrf_exempt
@require_POST
def save_chat_to_objects(request):
    try:
        data = json.loads(request.body)
        chat_id = data.get('chat_id')
        
        if not chat_id:
            return JsonResponse({'success': False, 'error': 'ID чата не указан'})
        
        user_profile, created = UserProfile.objects.get_or_create(user=request.user)
        organizations = user_profile.organizations.all()
        
        from django.db.models import Q
        objects = Objekt.objects.filter(
            Q(organizacii__in=organizations) | Q(otvetstvennyj__icontains=request.user.get_full_name()),
            chat_id__isnull=True
        ).distinct()
        
        updated_count = 0
        for obj in objects:
            obj.chat_id = chat_id
            obj.save()
            updated_count += 1
        
        return JsonResponse({
            'success': True,
            'updated_count': updated_count
        })
        
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)})
@csrf_exempt
@require_POST
def remove_chat_from_objects(request):
    try:
        data = json.loads(request.body)
        chat_id = data.get('chat_id')
        
        if not chat_id:
            return JsonResponse({'success': False, 'error': 'ID чата не указан'})
        
        user_profile, created = UserProfile.objects.get_or_create(user=request.user)
        organizations = user_profile.organizations.all()
        
        from django.db.models import Q
        objects = Objekt.objects.filter(
            Q(organizacii__in=organizations) | Q(otvetstvennyj__icontains=request.user.get_full_name()),
            chat_id=chat_id
        ).distinct()
        
        updated_count = 0
        for obj in objects:
            obj.chat_id = None
            obj.save()
            updated_count += 1
        
        return JsonResponse({
            'success': True,
            'updated_count': updated_count
        })
        
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)})