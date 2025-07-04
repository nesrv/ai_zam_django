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

def generate_documents(request):
    from django.conf import settings
    import os
    
    # Создаем папку для документов
    docs_dir = os.path.join(settings.MEDIA_ROOT, 'documents')
    os.makedirs(docs_dir, exist_ok=True)
    
    # Проходим по всем сотрудникам
    for sotrudnik in Sotrudnik.objects.all():
        dokumenty, created = DokumentySotrudnika.objects.get_or_create(sotrudnik=sotrudnik)
        
        # Создаем должностную инструкцию
        filename = f"dolzhn_instr_{sotrudnik.fio.replace(' ', '_')}.docx"
        file_path = os.path.join(docs_dir, filename)
        
        # Создаем пустой файл (в реальности здесь бы была генерация docx)
        with open(file_path, 'w') as f:
            f.write(f"Должностная инструкция для {sotrudnik.fio}")
        
        # Создаем запись в базе
        InstrukciiKartochki.objects.get_or_create(
            dokumenty_sotrudnika=dokumenty,
            nazvanie="Должностная инструкция",
            defaults={
                'tekst_kartochki': f"Должностная инструкция для {sotrudnik.fio}",
                'file_path': f"documents/{filename}"
            }
        )
    
    return JsonResponse({'success': True, 'message': 'Документы созданы'})

def download_document(request, sotrudnik_id, doc_type):
    from django.http import FileResponse, Http404, HttpResponse
    from django.conf import settings
    import os
    import tempfile
    
    sotrudnik = get_object_or_404(Sotrudnik, pk=sotrudnik_id)
    
    if doc_type == 'dolzhnostnaya':
        # Путь к шаблону
        template_path = os.path.join(settings.BASE_DIR, 'templates', 'documents', 'dolzhn_instr.txt')
        
        # Отображаем HTML-шаблон
        return render(request, 'sotrudniki/dolzhn_instr.html', {'sotrudnik': sotrudnik})
    
    raise Http404("Файл не найден")


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