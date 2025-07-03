from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from django.db.models import Sum
from datetime import datetime, timedelta
import json
from .models import ResursyPoObjektu, FakticheskijResursPoObjektu, DokhodResursa, Objekt

@csrf_exempt
@require_POST
def get_income_totals(request):
    try:
        data = json.loads(request.body)
        object_id = data.get('object_id')
        
        objekt = Objekt.objects.get(id=object_id)
        
        # Получаем ресурсы подрядных организаций
        resources = ResursyPoObjektu.objects.filter(
            objekt=objekt,
            resurs__kategoriya_resursa__nazvanie='Подрядные организации'
        ).select_related('resurs', 'resurs__kategoriya_resursa')
        
        # Фактические ресурсы
        fakticheskij_resursy = FakticheskijResursPoObjektu.objects.filter(
            resurs_po_objektu__objekt=objekt,
            resurs_po_objektu__resurs__kategoriya_resursa__nazvanie='Подрядные организации'
        ).select_related('resurs_po_objektu', 'resurs_po_objektu__resurs')
        
        # Доходы по фактическим ресурсам
        dokhody = {}
        for fr in fakticheskij_resursy:
            dokhody_list = DokhodResursa.objects.filter(fakticheskij_resurs=fr).order_by('-data')
            dokhody[fr.id] = dokhody_list
        
        # Создаем 20 дней
        today = datetime.now().date()
        days = [today - timedelta(days=i) for i in range(20)]
        
        # Вычисляем суммы по дням (аналогично object_income_detail)
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
        
        return JsonResponse({
            'success': True,
            'daily_totals': daily_totals
        })
        
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)})