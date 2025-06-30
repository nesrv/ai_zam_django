from django import template

register = template.Library()

@register.filter
def get_item(dictionary, key):
    """Получает элемент из словаря по ключу"""
    return dictionary.get(key, [])

@register.filter
def multiply(value, arg):
    """Умножает значение на аргумент"""
    try:
        return float(value) * float(arg)
    except (ValueError, TypeError):
        return 0
        
@register.filter
def subtract(value, arg):
    """Вычитает аргумент из значения"""
    try:
        return float(value) - float(arg)
    except (ValueError, TypeError):
        return value

@register.filter
def format_number(value):
    """Форматирует число с разделителями тысяч"""
    try:
        num = float(value)
        return "{:,.0f}".format(num).replace(",", " ")
    except (ValueError, TypeError):
        return value

@register.filter
def get_category_sum(category_name, resources):
    """Вычисляет сумму для категории"""
    total = 0
    for resource in resources:
        if resource.resurs.kategoriya_resursa.nazvanie == category_name:
            total += resource.kolichestvo * resource.cena
    return total

@register.filter
def get_resource_spent(resource_id, context):
    """Вычисляет общую сумму расходов по ресурсу"""
    total = 0
    fakticheskij_resursy = context.get('fakticheskij_resursy', [])
    raskhody = context.get('raskhody', {})
    
    for fr in fakticheskij_resursy:
        if fr.resurs_po_objektu.id == resource_id:
            for rashod in raskhody.get(fr.id, []):
                total += rashod.izraskhodovano
    return total

@register.filter
def get_daily_total(daily_totals, day):
    """Получает сумму для конкретной даты из словаря daily_totals"""
    day_key = day.strftime('%Y-%m-%d')
    return daily_totals.get(day_key, 0)

@register.filter
def calculate_daily_total(category, context):
    """Вычисляет сумму фактических расходов по дню для категории"""
    day = context.get('day')
    resources = context.get('resources')
    fakticheskij_resursy = context.get('fakticheskij_resursy')
    raskhody = context.get('raskhody')
    
    if not day or not resources or not fakticheskij_resursy or not raskhody:
        return 0
    
    total = 0
    day_key = day.strftime('%Y-%m-%d')
    
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
                        total += float(resource.cena) * float(rashod.izraskhodovano)
                break
    
    return total