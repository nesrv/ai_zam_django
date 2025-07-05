from django.shortcuts import render, get_object_or_404, redirect
from django.http import JsonResponse
from .models import Organizaciya, Sotrudnik, DokumentySotrudnika, InstrukciiKartochki, ProtokolyObucheniya, Instruktazhi, Podrazdelenie, Specialnost, ShablonyDokumentovPoSpecialnosti
from django.conf import settings
import os


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
    
    sotrudnik = get_object_or_404(Sotrudnik, pk=sotrudnik_id)
    
    if doc_type == 'dolzhnostnaya':
        # Проверяем есть ли шаблоны документов у специальности
        if sotrudnik.specialnost and hasattr(sotrudnik.specialnost, 'shablony_dokumentov'):
            shablony = sotrudnik.specialnost.shablony_dokumentov
            if shablony.dolzhnostnaya_instrukciya:
                # Читаем HTML файл должностной инструкции
                with open(shablony.dolzhnostnaya_instrukciya.path, 'r', encoding='utf-8') as f:
                    html_content = f.read()
                # Заменяем плейсхолдеры
                html_content = html_content.replace('{{ sotrudnik.fio }}', sotrudnik.fio)
                specialnost_name = sotrudnik.specialnost.nazvanie if sotrudnik.specialnost else 'Не указана'
                html_content = html_content.replace('{{ sotrudnik.specialnost|default:"Не указана" }}', specialnost_name)
                html_content = html_content.replace('{{ sotrudnik.specialnost }}', specialnost_name)
                return HttpResponse(html_content, content_type='text/html')
        
        # Используем стандартный шаблон
        return render(request, 'sotrudniki/dolzhn_instr.html', {'sotrudnik': sotrudnik})
    
    elif doc_type == 'kartochka':
        # Проверяем есть ли шаблон личной карточки
        html_content = None
        
        if sotrudnik.specialnost and hasattr(sotrudnik.specialnost, 'shablony_dokumentov'):
            shablony = sotrudnik.specialnost.shablony_dokumentov
            if shablony.lichnaya_kartochka_rabotnika:
                # Читаем HTML файл личной карточки
                with open(shablony.lichnaya_kartochka_rabotnika.path, 'r', encoding='utf-8') as f:
                    html_content = f.read()
        
        # Если шаблон не найден, используем шаблон по умолчанию
        if not html_content:
            default_template_path = os.path.join(settings.MEDIA_ROOT, 'instruction_templates', 'lichnaya_kartochka_podsobnyj.html')
            if os.path.exists(default_template_path):
                with open(default_template_path, 'r', encoding='utf-8') as f:
                    html_content = f.read()
            else:
                raise Http404("Шаблон личной карточки не найден")
        
        # Заменяем плейсхолдеры
        html_content = html_content.replace('{{ sotrudnik.fio }}', sotrudnik.fio)
        html_content = html_content.replace('{{ sotrudnik.data_rozhdeniya|date:"d.m.Y" }}', sotrudnik.data_rozhdeniya.strftime('%d.%m.%Y'))
        html_content = html_content.replace('{{ sotrudnik.data_priema|date:"d.m.Y" }}', sotrudnik.data_priema.strftime('%d.%m.%Y'))
        html_content = html_content.replace('{{ sotrudnik.data_nachala_raboty|date:"d.m.Y" }}', sotrudnik.data_nachala_raboty.strftime('%d.%m.%Y'))
        
        # Заменяем специальность
        specialnost_name = sotrudnik.specialnost.nazvanie if sotrudnik.specialnost else 'Не указана'
        html_content = html_content.replace('{{ sotrudnik.specialnost }}', specialnost_name)
        
        # Заменяем подразделение
        podrazdelenie_name = sotrudnik.podrazdelenie.nazvanie if sotrudnik.podrazdelenie else 'Строительное управление'
        html_content = html_content.replace('{{ sotrudnik.podrazdelenie.nazvanie|default:"Строительное управление" }}', podrazdelenie_name)
        
        return HttpResponse(html_content, content_type='text/html')
    
    elif doc_type == 'siz':
        # Проверяем есть ли шаблон личной карточки СИЗ
        html_content = None
        
        if sotrudnik.specialnost and hasattr(sotrudnik.specialnost, 'shablony_dokumentov'):
            shablony = sotrudnik.specialnost.shablony_dokumentov
            if shablony.lichnaya_kartochka_siz:
                # Читаем HTML файл личной карточки СИЗ
                with open(shablony.lichnaya_kartochka_siz.path, 'r', encoding='utf-8') as f:
                    html_content = f.read()
        
        # Если шаблон не найден, используем шаблон по умолчанию для "Подсобный рабочий"
        if not html_content:
            try:
                from .models import ShablonyDokumentovPoSpecialnosti, Specialnost
                default_specialnost = Specialnost.objects.get(nazvanie="Подсобный рабочий")
                default_shablony = ShablonyDokumentovPoSpecialnosti.objects.get(specialnost=default_specialnost)
                if default_shablony.lichnaya_kartochka_siz:
                    with open(default_shablony.lichnaya_kartochka_siz.path, 'r', encoding='utf-8') as f:
                        html_content = f.read()
            except:
                # Используем стандартный шаблон
                default_template_path = os.path.join(settings.MEDIA_ROOT, 'document_templates', 'lichnaya_kartochka_siz_alpinist_gazores.html')
                if os.path.exists(default_template_path):
                    with open(default_template_path, 'r', encoding='utf-8') as f:
                        html_content = f.read()
        
        if not html_content:
            raise Http404("Шаблон личной карточки СИЗ не найден")
        
        # Заменяем плейсхолдеры
        html_content = html_content.replace('{{ sotrudnik.fio }}', sotrudnik.fio)
        specialnost_name = sotrudnik.specialnost.nazvanie if sotrudnik.specialnost else 'Не указана'
        html_content = html_content.replace('{{ sotrudnik.specialnost }}', specialnost_name)
        html_content = html_content.replace('{{ sotrudnik.pol }}', sotrudnik.pol or '')
        html_content = html_content.replace('{{ sotrudnik.razmer_odezhdy }}', sotrudnik.razmer_odezhdy)
        html_content = html_content.replace('{{ sotrudnik.razmer_golovnogo_ubora }}', sotrudnik.razmer_golovnogo_ubora)
        html_content = html_content.replace('{{ sotrudnik.razmer_obuvi }}', sotrudnik.razmer_obuvi)
        html_content = html_content.replace('{{ sotrudnik.data_priema|date:"d.m.Y" }}', sotrudnik.data_priema.strftime('%d.%m.%Y'))
        
        return HttpResponse(html_content, content_type='text/html')
    
    raise Http404("Файл не найден")


def organizations_list(request):
    organizacii = Organizaciya.objects.filter(is_active=True)
    return render(request, 'sotrudniki/organizations.html', {'organizacii': organizacii})


def organization_detail(request, pk):
    organizaciya = get_object_or_404(Organizaciya, pk=pk)
    sotrudniki = Sotrudnik.objects.filter(organizaciya=organizaciya).select_related('specialnost', 'podrazdelenie')
    podrazdeleniya = organizaciya.podrazdeleniya.all()
    return render(request, 'sotrudniki/organization_detail.html', {
        'organizaciya': organizaciya,
        'sotrudniki': sotrudniki,
        'podrazdeleniya': podrazdeleniya
    })


def sotrudnik_add(request):
    if request.method == 'POST':
        fio = request.POST.get('fio')
        data_rozhdeniya = request.POST.get('data_rozhdeniya')
        data_priema = request.POST.get('data_priema')
        data_nachala_raboty = request.POST.get('data_nachala_raboty')
        specialnost_id = request.POST.get('specialnost')
        podrazdelenie_id = request.POST.get('podrazdelenie')
        organizaciya_id = request.POST.get('organizaciya')
        
        sotrudnik = Sotrudnik.objects.create(
            fio=fio,
            data_rozhdeniya=data_rozhdeniya,
            data_priema=data_priema,
            data_nachala_raboty=data_nachala_raboty,
            specialnost_id=specialnost_id if specialnost_id else None,
            podrazdelenie_id=podrazdelenie_id if podrazdelenie_id else None,
            organizaciya_id=organizaciya_id if organizaciya_id else None
        )
        
        if podrazdelenie_id:
            return redirect(f'/sotrudniki/?podrazdelenie={podrazdelenie_id}')
        return redirect('/sotrudniki/')
    
    podrazdelenie_id = request.GET.get('podrazdelenie')
    podrazdelenie = None
    if podrazdelenie_id:
        podrazdelenie = get_object_or_404(Podrazdelenie, pk=podrazdelenie_id)
    
    organizacii = Organizaciya.objects.filter(is_active=True)
    podrazdeleniya = Podrazdelenie.objects.all()
    specialnosti = Specialnost.objects.all()
    
    return render(request, 'sotrudniki/add.html', {
        'organizacii': organizacii,
        'podrazdeleniya': podrazdeleniya,
        'specialnosti': specialnosti,
        'selected_podrazdelenie': podrazdelenie
    })