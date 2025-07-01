from django.shortcuts import render, get_object_or_404
from django.db.models import Sum, Count, F
from .models import Objekt, ResursyPoObjektu, RaskhodResursa, Resurs, Kadry, FakticheskijResursPoObjektu, DokhodResursa
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
    
    # Словарь для итоговых сумм по дням (баланс)
    total_daily_balance = {}
    
    # Словари для данных доходов и расходов по дням
    daily_income_data = {}
    daily_expense_data = {}
    
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
        
        # Вычисляем баланс по дням (доходы - расходы)
        daily_balance = {}
        for day in days:
            day_key = day.strftime('%Y-%m-%d')
            income = daily_income.get(day_key, 0.0)
            expense = daily_expenses.get(day_key, 0.0)
            daily_balance[day_key] = income - expense
        
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
        
        # Сохраняем данные по дням для графика и итогов
        for day in days:
            day_key = day.strftime('%Y-%m-%d')
            
            # Расходы
            if day_key not in daily_expense_data:
                daily_expense_data[day_key] = 0.0
            daily_expense_data[day_key] += daily_expenses.get(day_key, 0.0)
            
            # Доходы
            if day_key not in daily_income_data:
                daily_income_data[day_key] = 0.0
            daily_income_data[day_key] += daily_income.get(day_key, 0.0)
            
            # Баланс (доходы - расходы)
            if day_key not in total_daily_balance:
                total_daily_balance[day_key] = 0.0
            total_daily_balance[day_key] += daily_balance.get(day_key, 0.0)
    
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
        
        # Подготавливаем данные для графика
        day_labels = [day.strftime('%d.%m') for day in days]
        x = range(len(day_labels))
        
        # Создаем данные для графика по формуле доход-расход
        income_values = []
        expense_values = []
        balance_values = []
        
        for day in days:
            day_key = day.strftime('%Y-%m-%d')
            
            # Доходы (из ячеек "Итого фактических расходов по дням" со страницы доходов)
            income = daily_income_data.get(day_key, 0.0)
            income_values.append(income / 1000)  # Конвертируем в тысячи рублей
            
            # Расходы (из ячеек "Итого фактических расходов по дням" со страницы расходов)
            expense = daily_expense_data.get(day_key, 0.0)
            expense_values.append(expense / 1000)  # Конвертируем в тысячи рублей
            
            # Баланс по формуле доход-расход
            balance = (income - expense) / 1000  # Конвертируем в тысячи рублей
            balance_values.append(balance)
        

        
        # Рисуем линии
        ax.plot(x, income_values, 'o-', linewidth=3, markersize=8, label='Доходы', color='#2ecc71', alpha=0.9)
        ax.plot(x, expense_values, 's-', linewidth=3, markersize=8, label='Расходы', color='#e74c3c', alpha=0.9)
        ax.plot(x, balance_values, '^-', linewidth=4, markersize=10, label='Баланс (доход-расход)', color='#3498db', alpha=1.0)
        
        # Добавляем подписи значений к точкам
        for i, (income, expense, balance) in enumerate(zip(income_values, expense_values, balance_values)):
            # Подписи для доходов (каждая 3-я точка, чтобы не перегружать график)
            if i % 3 == 0 and income > 0:
                ax.annotate(f'{income:.1f} тыс.₽', 
                           xy=(i, income), 
                           xytext=(i, income + max(income_values + expense_values) * 0.02),
                           fontsize=8, color='#2ecc71', weight='bold',
                           ha='center', va='bottom',
                           bbox=dict(boxstyle='round,pad=0.2', facecolor='black', alpha=0.6))
            
            # Подписи для расходов (каждая 3-я точка)
            if i % 3 == 0 and expense > 0:
                ax.annotate(f'{expense:.1f} тыс.₽', 
                           xy=(i, expense), 
                           xytext=(i, expense - max(income_values + expense_values) * 0.02),
                           fontsize=8, color='#e74c3c', weight='bold',
                           ha='center', va='top',
                           bbox=dict(boxstyle='round,pad=0.2', facecolor='black', alpha=0.6))
            
            # Подписи для баланса (каждая 2-я точка)
            if i % 2 == 0 and abs(balance) > max(income_values + expense_values) * 0.01:  # Только если баланс значимый
                ax.annotate(f'{balance:.1f} тыс.₽', 
                           xy=(i, balance), 
                           xytext=(i, balance + (10 if balance >= 0 else -10)),
                           fontsize=9, color='#3498db', weight='bold',
                           ha='center', va='bottom' if balance >= 0 else 'top',
                           bbox=dict(boxstyle='round,pad=0.3', facecolor='#2c3e50', alpha=0.8))
        
        # Добавляем подписи к линиям (последние точки)
        if income_values:
            last_income = income_values[-1]
            ax.annotate(f'Доходы: {last_income:.1f} тыс.₽', 
                       xy=(x[-1], last_income), 
                       xytext=(x[-1] + 0.5, last_income),
                       fontsize=10, color='#2ecc71', weight='bold',
                       bbox=dict(boxstyle='round,pad=0.3', facecolor='black', alpha=0.7),
                       arrowprops=dict(arrowstyle='->', color='#2ecc71', alpha=0.7))
        
        if expense_values:
            last_expense = expense_values[-1]
            ax.annotate(f'Расходы: {last_expense:.1f} тыс.₽', 
                       xy=(x[-1], last_expense), 
                       xytext=(x[-1] + 0.5, last_expense - max(income_values + expense_values) * 0.1),
                       fontsize=10, color='#e74c3c', weight='bold',
                       bbox=dict(boxstyle='round,pad=0.3', facecolor='black', alpha=0.7),
                       arrowprops=dict(arrowstyle='->', color='#e74c3c', alpha=0.7))
        
        if balance_values:
            last_balance = balance_values[-1]
            ax.annotate(f'Баланс: {last_balance:.1f} тыс.₽', 
                       xy=(x[-1], last_balance), 
                       xytext=(x[-1] + 0.5, last_balance + max(income_values + expense_values) * 0.1),
                       fontsize=12, color='#3498db', weight='bold',
                       bbox=dict(boxstyle='round,pad=0.5', facecolor='#2c3e50', alpha=0.9),
                       arrowprops=dict(arrowstyle='->', color='#3498db', alpha=0.9))
        
        # Добавляем горизонтальную линию для нулевого баланса
        ax.axhline(y=0, color='#ffffff', linestyle='--', alpha=0.5, linewidth=1)
        ax.annotate('Нулевой баланс', xy=(len(x)-1, 0), xytext=(len(x)-2, max(income_values + expense_values) * 0.05),
                   fontsize=10, color='#ffffff', alpha=0.7,
                   bbox=dict(boxstyle='round,pad=0.2', facecolor='black', alpha=0.5),
                   arrowprops=dict(arrowstyle='->', color='#ffffff', alpha=0.5))
        
        ax.set_xlabel('Дни', fontsize=12, color='white')
        ax.set_ylabel('Сумма (тыс. ₽)', fontsize=12, color='white')
        ax.set_title('Баланс доходов и расходов по дням (доход-расход)', fontsize=14, color='white', pad=20)
        ax.set_xticks(x)
        ax.set_xticklabels(day_labels, rotation=45, ha='right', fontsize=10)
        
        # Форматирование оси Y в тысячах рублей
        from matplotlib.ticker import FuncFormatter
        def thousands_formatter(x, pos):
            return f'{x:.0f}'
        ax.yaxis.set_major_formatter(FuncFormatter(thousands_formatter))
        
        ax.legend(bbox_to_anchor=(1.05, 1), loc='upper left')
        ax.grid(True, alpha=0.3)
        
        # Настройка внешнего вида
        plt.tight_layout()
        
        # Сохраняем график с временной меткой для избежания кэширования
        charts_dir = os.path.join(settings.BASE_DIR, 'static', 'charts')
        os.makedirs(charts_dir, exist_ok=True)
        
        # Удаляем старые файлы графиков (оставляем только последние 5)
        old_charts = [f for f in os.listdir(charts_dir) if f.startswith('profit_balance_chart_')]
        old_charts.sort(reverse=True)
        for old_chart in old_charts[5:]:  # Удаляем все кроме последних 5
            try:
                os.remove(os.path.join(charts_dir, old_chart))
            except:
                pass
        
        timestamp = int(time.time())
        chart_filename = f'profit_balance_chart_{timestamp}.png'
        chart_path = os.path.join(charts_dir, chart_filename)
        
        plt.savefig(chart_path, dpi=300, bbox_inches='tight', facecolor='#1a1a1a')
        plt.close()
        
        # Проверяем, что файл создался
        if os.path.exists(chart_path):
            print(f"График успешно создан: {chart_path}")
        else:
            print(f"Ошибка: файл не создан: {chart_path}")
        
        return f'charts/{chart_filename}'
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
    
    context = {
        'object': obj,
        'resources': resources,
        'total_cost': total_cost,
        'fakticheskij_resursy': fakticheskij_resursy,
        'raskhody': raskhody,
        'total_spent': total_spent,
        'days': days,
        'category_daily_totals': category_daily_totals,
        'total_daily_expenses': total_daily_expenses,
    }
    
    return render(request, 'object/object_detail.html', context)

def object_income_detail(request, object_id):
    # Получаем объект или 404
    obj = get_object_or_404(Objekt.objects.select_related('otvetstvennyj'), id=object_id)
    
    # Получаем только ресурсы категории "Подрядные организации"
    resources = ResursyPoObjektu.objects.filter(
        objekt=obj,
        resurs__kategoriya_resursa__nazvanie='Подрядные организации'
    ).select_related('resurs', 'resurs__kategoriya_resursa')
    
    # Суммарная стоимость ресурсов
    total_cost = sum(float(r.kolichestvo * r.cena) for r in resources)
    
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

