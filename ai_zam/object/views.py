from django.shortcuts import render
from .models import Objekt, ResursyPoObjektu

def home(request):
    # Получаем статистику для главной страницы
    total_objects = Objekt.objects.count()
    active_objects = Objekt.objects.filter(status='в работе').count()
    completed_objects = Objekt.objects.filter(status='завершён').count()
    
    # Последние объекты
    recent_objects = Objekt.objects.order_by('-id')[:5]
    
    context = {
        'total_objects': total_objects,
        'active_objects': active_objects,
        'completed_objects': completed_objects,
        'recent_objects': recent_objects,
    }
    
    return render(request, 'object/home.html', context)