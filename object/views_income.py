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
    max_retries = 3
    retry_delay = 0.1
    
    for attempt in range(max_retries):
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
            error_msg = str(e)
            if 'database is locked' in error_msg.lower() and attempt < max_retries - 1:
                time.sleep(retry_delay)
                retry_delay *= 2
                continue
            else:
                return JsonResponse({'success': False, 'error': error_msg})
    
    return JsonResponse({'success': False, 'error': 'Database is locked after multiple attempts'})