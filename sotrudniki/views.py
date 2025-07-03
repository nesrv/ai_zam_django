from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse
from .models import Organizaciya, Sotrudnik, DokumentySotrudnika, InstrukciiKartochki, ProtokolyObucheniya, Instruktazhi


def sotrudniki_list(request):
    sotrudniki = Sotrudnik.objects.select_related('organizaciya', 'specialnost', 'podrazdelenie').all()
    
    podrazdelenie_id = request.GET.get('podrazdelenie')
    if podrazdelenie_id:
        sotrudniki = sotrudniki.filter(podrazdelenie_id=podrazdelenie_id)
    
    return render(request, 'sotrudniki/list.html', {'sotrudniki': sotrudniki})


def sotrudnik_detail(request, pk):
    sotrudnik = get_object_or_404(Sotrudnik, pk=pk)
    dokumenty, created = DokumentySotrudnika.objects.get_or_create(sotrudnik=sotrudnik)
    
    instrukcii = InstrukciiKartochki.objects.filter(dokumenty_sotrudnika=dokumenty)
    protokoly = ProtokolyObucheniya.objects.filter(dokumenty_sotrudnika=dokumenty)
    instruktazhi = Instruktazhi.objects.filter(dokumenty_sotrudnika=dokumenty)
    
    tab = request.GET.get('tab', 'documents')
    
    context = {
        'sotrudnik': sotrudnik,
        'instrukcii': instrukcii,
        'protokoly': protokoly,
        'instruktazhi': instruktazhi,
        'active_tab': tab,
    }
    return render(request, 'sotrudniki/detail.html', context)


def update_document_status(request):
    if request.method == 'POST':
        doc_type = request.POST.get('doc_type')
        doc_id = request.POST.get('doc_id')
        field = request.POST.get('field')
        value = request.POST.get('value') == 'true'
        
        if doc_type == 'instrukcii':
            doc = get_object_or_404(InstrukciiKartochki, pk=doc_id)
        elif doc_type == 'protokoly':
            doc = get_object_or_404(ProtokolyObucheniya, pk=doc_id)
        elif doc_type == 'instruktazhi':
            doc = get_object_or_404(Instruktazhi, pk=doc_id)
        else:
            return JsonResponse({'success': False})
        
        if field in ['soglasovan', 'raspechatn']:
            setattr(doc, field, value)
            doc.save()
            return JsonResponse({'success': True})
    
    return JsonResponse({'success': False})


def organizations_list(request):
    organizacii = Organizaciya.objects.all()
    return render(request, 'sotrudniki/organizations.html', {'organizacii': organizacii})


def organization_detail(request, pk):
    organizaciya = get_object_or_404(Organizaciya, pk=pk)
    sotrudniki = Sotrudnik.objects.filter(organizaciya=organizaciya).select_related('specialnost', 'podrazdelenie')
    from .models import Podrazdelenie
    podrazdeleniya = Podrazdelenie.objects.all()
    return render(request, 'sotrudniki/organization_detail.html', {
        'organizaciya': organizaciya,
        'sotrudniki': sotrudniki,
        'podrazdeleniya': podrazdeleniya
    })