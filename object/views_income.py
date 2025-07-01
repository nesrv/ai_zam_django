from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from django.db.models import Sum
from datetime import datetime
import json
import time
from .models import ResursyPoObjektu, FakticheskijResursPoObjektu, DokhodResursa

@csrf_exempt
@require_POST
def update_income(request):
    try:
        data = json.loads(request.body)
        resource_id = data.get('resource_id')
        date_str = data.get('date')
        amount = float(data.get('amount', 0))
        
        resource = ResursyPoObjektu.objects.get(id=resource_id)
        
        fakticheskij_resurs, created = FakticheskijResursPoObjektu.objects.get_or_create(
            resurs_po_objektu=resource
        )
        
        date_obj = datetime.strptime(date_str, '%Y-%m-%d').date()
        
        dokhod, created = DokhodResursa.objects.update_or_create(
            fakticheskij_resurs=fakticheskij_resurs,
            data=date_obj,
            defaults={'vypolneno': amount}
        )
        
        total_completed = DokhodResursa.objects.filter(
            fakticheskij_resurs=fakticheskij_resurs
        ).aggregate(total=Sum('vypolneno'))['total'] or 0
        
        resource.potracheno = total_completed
        resource.save()
        
        return JsonResponse({
            'success': True,
            'potracheno': float(total_completed),
            'ostatok': float(resource.kolichestvo - total_completed)
        })
        
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)})