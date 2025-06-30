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