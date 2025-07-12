from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from .models import Objekt, ResursyPoObjektu, FakticheskijResursPoObjektu, RaskhodResursa, DokhodResursa, SvodnayaRaskhodDokhodPoDnyam
from sotrudniki.models import Sotrudnik

def export_object_json(request, object_id):
    obj = get_object_or_404(Objekt, id=object_id)
    
    # Основные данные объекта
    object_data = {
        'id': obj.id,
        'nazvanie': obj.nazvanie,
        'data_nachala': obj.data_nachala.isoformat() if obj.data_nachala else None,
        'data_plan_zaversheniya': obj.data_plan_zaversheniya.isoformat() if obj.data_plan_zaversheniya else None,
        'data_fakt_zaversheniya': obj.data_fakt_zaversheniya.isoformat() if obj.data_fakt_zaversheniya else None,
        'status': obj.status,
        'otvetstvennyj': obj.otvetstvennyj,
        'is_active': obj.is_active,
        'organizaciya': {
            'id': obj.organizaciya.id if obj.organizaciya else None,
            'nazvanie': obj.organizaciya.nazvanie if obj.organizaciya else None,
            'inn': obj.organizaciya.inn if obj.organizaciya else None,
            'ogrn': obj.organizaciya.ogrn if obj.organizaciya else None,
            'adres': obj.organizaciya.adres if obj.organizaciya else None,
            'is_active': obj.organizaciya.is_active if obj.organizaciya else None,
        } if obj.organizaciya else None,
    }
    
    # Ресурсы по объекту
    resources = ResursyPoObjektu.objects.filter(objekt=obj).select_related('resurs', 'resurs__kategoriya_resursa')
    resources_data = []
    
    for resource in resources:
        resource_data = {
            'id': resource.id,
            'kolichestvo': float(resource.kolichestvo),
            'cena': float(resource.cena),
            'potracheno': float(resource.potracheno),
            'resurs': {
                'id': resource.resurs.id,
                'naimenovanie': resource.resurs.naimenovanie,
                'edinica_izmereniya': resource.resurs.edinica_izmereniya,
                'kategoriya_resursa': {
                    'id': resource.resurs.kategoriya_resursa.id,
                    'nazvanie': resource.resurs.kategoriya_resursa.nazvanie,
                    'raskhod_dokhod': resource.resurs.kategoriya_resursa.raskhod_dokhod,
                }
            }
        }
        
        # Фактические ресурсы
        try:
            fakt_resurs = FakticheskijResursPoObjektu.objects.get(resurs_po_objektu=resource)
            
            # Расходы
            raskhody = RaskhodResursa.objects.filter(fakticheskij_resurs=fakt_resurs)
            raskhody_data = []
            for rashod in raskhody:
                raskhody_data.append({
                    'id': rashod.id,
                    'data': rashod.data.isoformat(),
                    'izraskhodovano': float(rashod.izraskhodovano)
                })
            
            # Доходы
            dokhody = DokhodResursa.objects.filter(fakticheskij_resurs=fakt_resurs)
            dokhody_data = []
            for dokhod in dokhody:
                dokhody_data.append({
                    'id': dokhod.id,
                    'data': dokhod.data.isoformat(),
                    'vypolneno': float(dokhod.vypolneno)
                })
            
            resource_data['fakticheskij_resurs'] = {
                'id': fakt_resurs.id,
                'raskhody': raskhody_data,
                'dokhody': dokhody_data
            }
        except FakticheskijResursPoObjektu.DoesNotExist:
            resource_data['fakticheskij_resurs'] = None
        
        resources_data.append(resource_data)
    
    # Сотрудники по объекту
    employees = Sotrudnik.objects.filter(objekty=obj).select_related('specialnost', 'podrazdelenie', 'organizaciya')
    employees_data = []
    
    for emp in employees:
        employees_data.append({
            'id': emp.id,
            'fio': emp.fio,
            'data_rozhdeniya': emp.data_rozhdeniya.isoformat() if emp.data_rozhdeniya else None,
            'pol': emp.pol,
            'data_priema': emp.data_priema.isoformat() if emp.data_priema else None,
            'data_nachala_raboty': emp.data_nachala_raboty.isoformat() if emp.data_nachala_raboty else None,
            'specialnost': {
                'id': emp.specialnost.id if emp.specialnost else None,
                'nazvanie': emp.specialnost.nazvanie if emp.specialnost else None,
                'kategoriya': emp.specialnost.kategoriya if emp.specialnost else None,
            } if emp.specialnost else None,
            'podrazdelenie': {
                'id': emp.podrazdelenie.id if emp.podrazdelenie else None,
                'kod': emp.podrazdelenie.kod if emp.podrazdelenie else None,
                'nazvanie': emp.podrazdelenie.nazvanie if emp.podrazdelenie else None,
            } if emp.podrazdelenie else None,
            'organizaciya': {
                'id': emp.organizaciya.id if emp.organizaciya else None,
                'nazvanie': emp.organizaciya.nazvanie if emp.organizaciya else None,
                'inn': emp.organizaciya.inn if emp.organizaciya else None,
            } if emp.organizaciya else None,
        })
    
    # Сводная по дням
    svodnaya = SvodnayaRaskhodDokhodPoDnyam.objects.filter(objekt=obj)
    svodnaya_data = []
    
    for sv in svodnaya:
        svodnaya_data.append({
            'id': sv.id,
            'data': sv.data.isoformat(),
            'raskhod': float(sv.raskhod),
            'dokhod': float(sv.dokhod),
            'balans': float(sv.balans)
        })
    
    # Итоговый JSON
    result = {
        'objekt': object_data,
        'resursy_po_objektu': resources_data,
        'sotrudniki': employees_data,
        'svodnaya_raskhod_dokhod_po_dnyam': svodnaya_data
    }
    
    return JsonResponse(result, json_dumps_params={'ensure_ascii': False, 'indent': 2})