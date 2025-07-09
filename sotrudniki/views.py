from django.shortcuts import render, get_object_or_404, redirect
from django.http import JsonResponse
from .models import Organizaciya, Sotrudnik, ProtokolyObucheniya, Podrazdelenie, Specialnost, ShablonyDokumentovPoSpecialnosti, SotrudnikiShablonyProtokolov, Instruktazhi, ShablonyInstruktazhej
from django.conf import settings
from django.template import Template, Context
import os


def sotrudniki_list(request):
    sotrudniki = Sotrudnik.objects.select_related('organizaciya', 'specialnost', 'podrazdelenie').filter(organizaciya__is_active=True)
    
    podrazdelenie_id = request.GET.get('podrazdelenie')
    if podrazdelenie_id:
        sotrudniki = sotrudniki.filter(podrazdelenie_id=podrazdelenie_id)
    
    return render(request, 'sotrudniki/list.html', {'sotrudniki': sotrudniki})


def sotrudnik_detail(request, pk):
    sotrudnik = get_object_or_404(Sotrudnik, pk=pk)
    
    protokoly = ProtokolyObucheniya.objects.filter(sotrudnik=sotrudnik).select_related('shablon_protokola')
    
    tab = request.GET.get('tab', 'documents')
    
    context = {
        'sotrudnik': sotrudnik,
        'protokoly': protokoly,
        'active_tab': tab,
    }
    return render(request, 'sotrudniki/detail.html', context)


def sotrudnik_documents(request, pk):
    from .models import DokumentySotrudnika
    from datetime import date
    sotrudnik = get_object_or_404(Sotrudnik, pk=pk)
    
    # Автоматически создаем документы для сотрудника
    if sotrudnik.specialnost and hasattr(sotrudnik.specialnost, 'shablony_dokumentov'):
        shablony = sotrudnik.specialnost.shablony_dokumentov
        
        # Создаем документы если их еще нет
        doc_types = [
            ('dolzhnostnaya', shablony.dolzhnostnaya_instrukciya),
            ('kartochka', shablony.lichnaya_kartochka_rabotnika),
            ('siz', shablony.lichnaya_kartochka_siz),
            ('riski', shablony.karta_ocenki_riskov),
        ]
        
        for doc_type, template_file in doc_types:
            if template_file:
                DokumentySotrudnika.objects.get_or_create(
                    sotrudnik=sotrudnik,
                    tip_dokumenta=doc_type
                )
    
    # Автоматически создаем протоколы обучения
    protokoly_shablony = SotrudnikiShablonyProtokolov.objects.filter(specialnost=sotrudnik.specialnost)
    for shablon in protokoly_shablony:
        ProtokolyObucheniya.objects.get_or_create(
            sotrudnik=sotrudnik,
            shablon_protokola=shablon,
            defaults={
                'nomer_programmy': '2025/AA.00-0000',
                'data_prikaza': date.today(),
                'data_protokola_dopuska': date.today(),
                'data_dopuska_k_rabote': date.today(),
                'registracionnyy_nomer': f"{sotrudnik.id}-{shablon.id}"
            }
        )
    
    # Автоматически создаем инструктажи для сотрудника
    from datetime import date
    instruktazhi_shablony = ShablonyInstruktazhej.objects.filter(specialnost=sotrudnik.specialnost)
    for shablon in instruktazhi_shablony:
        Instruktazhi.objects.get_or_create(
            sotrudnik=sotrudnik,
            instruktazh=shablon,
            defaults={
                'data_provedeniya': date.today(),
                'instruktor': sotrudnik
            }
        )
    
    # Получаем созданные документы
    dokumenty = DokumentySotrudnika.objects.filter(sotrudnik=sotrudnik)
    protokoly = ProtokolyObucheniya.objects.filter(sotrudnik=sotrudnik).select_related('shablon_protokola')
    instruktazhi = Instruktazhi.objects.filter(sotrudnik=sotrudnik).select_related('instruktazh__specialnost', 'instruktor')
    
    context = {
        'sotrudnik': sotrudnik,
        'dokumenty': dokumenty,
        'protokoly': protokoly,
        'instruktazhi': instruktazhi,
    }
    return render(request, 'sotrudniki/documents.html', context)


def document_editor(request, pk, doc_type):
    from .models import DokumentySotrudnika
    from django.template import Template, Context
    from django.utils import translation
    
    sotrudnik = get_object_or_404(Sotrudnik, pk=pk)
    
    # Получаем HTML содержимое документа
    html_content = ""
    doc_title = ""
    protokol = None
    instruktazh = None
    
    if doc_type == 'instruktazh':
        # Получаем ID инструктажа из параметров запроса
        instruktazh_id = request.GET.get('id')
        if instruktazh_id:
            instruktazh = get_object_or_404(Instruktazhi.objects.select_related('instruktazh'), 
                                          id=instruktazh_id, sotrudnik=sotrudnik)
            if instruktazh.instruktazh.html_file:
                with open(instruktazh.instruktazh.html_file.path, 'r', encoding='utf-8') as f:
                    html_content = f.read()
                doc_title = f"Инструктаж: {instruktazh.instruktazh.get_tip_instruktazha_display()}"
    elif doc_type == 'protokol':
        # Получаем ID протокола из параметров запроса
        protokol_id = request.GET.get('id')
        if protokol_id:
            protokol = get_object_or_404(ProtokolyObucheniya.objects.select_related('shablon_protokola'), 
                                       id=protokol_id, sotrudnik=sotrudnik)
            if protokol.shablon_protokola.html_file:
                with open(protokol.shablon_protokola.html_file.path, 'r', encoding='utf-8') as f:
                    html_content = f.read()
                doc_title = f"Протокол: {protokol.shablon_protokola.kurs}"
    elif doc_type in ['dolzhnostnaya', 'kartochka', 'siz', 'riski']:
        if sotrudnik.specialnost and hasattr(sotrudnik.specialnost, 'shablony_dokumentov'):
            shablony = sotrudnik.specialnost.shablony_dokumentov
            
            if doc_type == 'dolzhnostnaya' and shablony.dolzhnostnaya_instrukciya:
                with open(shablony.dolzhnostnaya_instrukciya.path, 'r', encoding='utf-8') as f:
                    html_content = f.read()
                doc_title = "Должностная инструкция"
            elif doc_type == 'kartochka' and shablony.lichnaya_kartochka_rabotnika:
                with open(shablony.lichnaya_kartochka_rabotnika.path, 'r', encoding='utf-8') as f:
                    html_content = f.read()
                doc_title = "Личная карточка работника"
            elif doc_type == 'siz' and shablony.lichnaya_kartochka_siz:
                with open(shablony.lichnaya_kartochka_siz.path, 'r', encoding='utf-8') as f:
                    html_content = f.read()
                doc_title = "Личная карточка СИЗ"
            elif doc_type == 'riski' and shablony.karta_ocenki_riskov:
                with open(shablony.karta_ocenki_riskov.path, 'r', encoding='utf-8') as f:
                    html_content = f.read()
                doc_title = "Карта оценки рисков"
    
    # Рендерим HTML с использованием Django Template для корректной обработки переменных
    if html_content:
        try:
            # Активируем русскую локализацию для дат
            translation.activate('ru')
            
            template = Template(html_content)
            context = Context({
                'sotrudnik': sotrudnik,
                'protokol': protokol,
                'instruktazh': instruktazh
            })
            html_content = template.render(context)
        except Exception as e:
            # Если возникла ошибка при рендеринге, используем простую замену строк
            html_content = html_content.replace('{{ sotrudnik.fio }}', sotrudnik.fio)
            html_content = html_content.replace('{{ sotrudnik.specialnost }}', sotrudnik.specialnost.nazvanie if sotrudnik.specialnost else 'Не указана')
            if sotrudnik.data_rozhdeniya:
                html_content = html_content.replace('{{ sotrudnik.data_rozhdeniya|date:"d.m.Y" }}', sotrudnik.data_rozhdeniya.strftime('%d.%m.%Y'))
            if sotrudnik.data_priema:
                html_content = html_content.replace('{{ sotrudnik.data_priema|date:"d.m.Y" }}', sotrudnik.data_priema.strftime('%d.%m.%Y'))
            if sotrudnik.data_nachala_raboty:
                html_content = html_content.replace('{{ sotrudnik.data_nachala_raboty|date:"d.m.Y" }}', sotrudnik.data_nachala_raboty.strftime('%d.%m.%Y'))
            if sotrudnik.organizaciya:
                html_content = html_content.replace('{{ sotrudnik.organizaciya }}', sotrudnik.organizaciya.nazvanie)
                html_content = html_content.replace('{{ sotrudnik.organizaciya.adres }}', sotrudnik.organizaciya.adres or '')
                html_content = html_content.replace('{{ sotrudnik.organizaciya.ogrn }}', sotrudnik.organizaciya.ogrn or '')
                html_content = html_content.replace('{{ sotrudnik.organizaciya.inn }}', sotrudnik.organizaciya.inn or '')
    
    context = {
        'sotrudnik': sotrudnik,
        'doc_type': doc_type,
        'doc_title': doc_title,
        'html_content': html_content,
    }
    return render(request, 'sotrudniki/document_editor.html', context)


def update_document_status(request):
    if request.method == 'POST':
        doc_type = request.POST.get('doc_type')
        doc_id = request.POST.get('doc_id')
        field = request.POST.get('field')
        value = request.POST.get('value') == 'true'
        
        if doc_type == 'protokoly':
            doc = get_object_or_404(ProtokolyObucheniya, pk=doc_id)
        else:
            return JsonResponse({'success': False})
        
        if field in ['soglasovan', 'raspechatn']:
            setattr(doc, field, value)
            doc.save()
            return JsonResponse({'success': True})
    
    return JsonResponse({'success': False})

def generate_documents(request):
    return JsonResponse({'success': True, 'message': 'Функция временно отключена'})

def download_document(request, sotrudnik_id, doc_type, protokol_id=None):
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
    
    elif doc_type == 'riski':
        # Проверяем есть ли шаблон карты оценки рисков
        html_content = None
        
        if sotrudnik.specialnost and hasattr(sotrudnik.specialnost, 'shablony_dokumentov'):
            shablony = sotrudnik.specialnost.shablony_dokumentov
            if shablony.karta_ocenki_riskov:
                # Читаем HTML файл карты оценки рисков
                with open(shablony.karta_ocenki_riskov.path, 'r', encoding='utf-8') as f:
                    html_content = f.read()
        
        # Если шаблон не найден, используем стандартный шаблон
        if not html_content:
            default_template_path = os.path.join(settings.MEDIA_ROOT, 'document_templates', 'karta_ocenki_prof_riskov_template.html')
            if os.path.exists(default_template_path):
                with open(default_template_path, 'r', encoding='utf-8') as f:
                    html_content = f.read()
            else:
                raise Http404("Шаблон карты оценки рисков не найден")
        
        # Заменяем плейсхолдеры
        html_content = html_content.replace('{{ sotrudnik.fio }}', sotrudnik.fio)
        organizaciya_name = sotrudnik.organizaciya.nazvanie if sotrudnik.organizaciya else 'ООО "РАЗВИТИЕ"'
        html_content = html_content.replace('{{ sotrudnik.organizaciya }}', organizaciya_name)
        podrazdelenie_name = sotrudnik.podrazdelenie.nazvanie if sotrudnik.podrazdelenie else 'Строительное управление'
        html_content = html_content.replace('{{ sotrudnik.podrazdelenie }}', podrazdelenie_name)
        specialnost_name = sotrudnik.specialnost.nazvanie if sotrudnik.specialnost else 'Не указана'
        html_content = html_content.replace('{{ sotrudnik.specialnost }}', specialnost_name)
        html_content = html_content.replace('{{ sotrudnik.data_rozhdeniya|date:"d.m.Y" }}', sotrudnik.data_rozhdeniya.strftime('%d.%m.%Y'))
        html_content = html_content.replace('{{ sotrudnik.data_priema|date:"d.m.Y" }}', sotrudnik.data_priema.strftime('%d.%m.%Y'))
        html_content = html_content.replace('{{ sotrudnik.data_nachala_raboty|date:"d.m.Y" }}', sotrudnik.data_nachala_raboty.strftime('%d.%m.%Y'))
        
        return HttpResponse(html_content, content_type='text/html')
    
    elif doc_type == 'protokol':
        from django.template import Template, Context
        
        # Получаем ID протокола
        if not protokol_id:
            raise Http404("Протокол не найден")
        
        # Получаем протокол с связанным шаблоном
        protokol = get_object_or_404(ProtokolyObucheniya.objects.select_related('shablon_protokola'), 
                                   id=protokol_id, sotrudnik=sotrudnik)
        
        # Получаем HTML файл из шаблона
        if protokol.shablon_protokola.html_file:
            with open(protokol.shablon_protokola.html_file.path, 'r', encoding='utf-8') as f:
                html_content = f.read()
        else:
            raise Http404("Шаблон протокола не найден")
        
        # Создаем Django Template и рендерим с контекстом
        template = Template(html_content)
        context = Context({
            'sotrudnik': sotrudnik,
            'protokol': protokol
        })
        
        # Активируем русскую локализацию для дат
        from django.utils import translation
        translation.activate('ru')
        
        rendered_html = template.render(context)
        
        return HttpResponse(rendered_html, content_type='text/html')
    
    elif doc_type == 'ohrana':
        # Проверяем есть ли шаблон инструкции по охране труда
        html_content = None
        
        if sotrudnik.specialnost and hasattr(sotrudnik.specialnost, 'shablony_dokumentov'):
            shablony = sotrudnik.specialnost.shablony_dokumentov
            if shablony.instrukciya_po_ohrane_truda:
                # Читаем HTML файл инструкции по охране труда
                with open(shablony.instrukciya_po_ohrane_truda.path, 'r', encoding='utf-8') as f:
                    html_content = f.read()
        
        # Если шаблон не найден, используем стандартный шаблон
        if not html_content:
            default_template_path = os.path.join(settings.MEDIA_ROOT, 'document_templates', 'instrukciya_po_ohrane_truda_template.html')
            if os.path.exists(default_template_path):
                with open(default_template_path, 'r', encoding='utf-8') as f:
                    html_content = f.read()
            else:
                raise Http404("Шаблон инструкции по охране труда не найден")
        
        # Заменяем плейсхолдеры
        html_content = html_content.replace('{{ sotrudnik.fio }}', sotrudnik.fio)
        specialnost_name = sotrudnik.specialnost.nazvanie if sotrudnik.specialnost else 'Не указана'
        html_content = html_content.replace('{{ sotrudnik.specialnost }}', specialnost_name)
        html_content = html_content.replace('{{ sotrudnik.specialnost|upper }}', specialnost_name.upper())
        
        return HttpResponse(html_content, content_type='text/html')
    
    elif doc_type == 'instruktazh':
        from django.template import Template, Context
        
        if not protokol_id:
            raise Http404("Инструктаж не найден")
        
        instruktazh = get_object_or_404(Instruktazhi.objects.select_related('instruktazh', 'instruktor'), 
                                       id=protokol_id, sotrudnik=sotrudnik)
        
        if instruktazh.instruktazh.html_file:
            with open(instruktazh.instruktazh.html_file.path, 'r', encoding='utf-8') as f:
                html_content = f.read()
        else:
            raise Http404("Шаблон инструктажа не найден")
        
        template = Template(html_content)
        context = Context({
            'sotrudnik': sotrudnik,
            'instruktazh': instruktazh
        })
        
        rendered_html = template.render(context)
        return HttpResponse(rendered_html, content_type='text/html')
    
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
        pol = request.POST.get('pol')
        razmer_odezhdy = request.POST.get('razmer_odezhdy', '50-52')
        razmer_obuvi = request.POST.get('razmer_obuvi', '43')
        razmer_golovnogo_ubora = request.POST.get('razmer_golovnogo_ubora', '55')
        
        sotrudnik = Sotrudnik.objects.create(
            fio=fio,
            data_rozhdeniya=data_rozhdeniya,
            data_priema=data_priema,
            data_nachala_raboty=data_nachala_raboty,
            specialnost_id=specialnost_id if specialnost_id else None,
            podrazdelenie_id=podrazdelenie_id if podrazdelenie_id else None,
            organizaciya_id=organizaciya_id if organizaciya_id else None,
            pol=pol if pol else None,
            razmer_odezhdy=razmer_odezhdy,
            razmer_obuvi=razmer_obuvi,
            razmer_golovnogo_ubora=razmer_golovnogo_ubora
        )
        
        return redirect(f'/sotrudniki/{sotrudnik.id}/documents/')
    
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