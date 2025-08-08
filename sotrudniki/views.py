from django.shortcuts import render, get_object_or_404
from datetime import datetime, timedelta
from .models import SotrudnikiZarplaty
from django.shortcuts import redirect
from django.http import JsonResponse
from .models import Organizaciya, Sotrudnik, ProtokolyObucheniya, Podrazdelenie, Specialnost, ShablonyDokumentovPoSpecialnosti, SotrudnikiShablonyProtokolov, Instruktazhi, ShablonyInstruktazhej
from django.conf import settings
from django.template import Template, Context
from datetime import datetime
from django.contrib.auth.decorators import login_required
import os


def sotrudniki_list(request):
    if request.user.is_authenticated:
        from object.models import UserProfile, Objekt
        from django.db.models import Q
        user_profile, created = UserProfile.objects.get_or_create(user=request.user)
        user_organizations = user_profile.organizations.all()
        user_objects = Objekt.objects.filter(
            organizacii__in=user_organizations,
            is_active=True
        ).distinct()
        
        # Получаем сотрудников из организаций пользователя ИЛИ привязанных к объектам пользователя
        sotrudniki = Sotrudnik.objects.select_related('organizaciya', 'specialnost', 'podrazdelenie').filter(
            Q(organizaciya__in=user_organizations) | Q(objekty_work__in=user_objects)
        ).distinct()
    else:
        # Для неавторизованных пользователей показываем сотрудников, связанных с демо-организациями и демо-объектами
        from object.models import Objekt
        from django.db.models import Q
        demo_objects = Objekt.objects.filter(demo=True, is_active=True)
        demo_organizations = Organizaciya.objects.filter(demo=True, is_active=True)
        sotrudniki = Sotrudnik.objects.select_related('organizaciya', 'specialnost', 'podrazdelenie').filter(
            Q(organizaciya__in=demo_organizations) | Q(objekty_work__in=demo_objects)
        ).distinct()
    
    podrazdelenie_id = request.GET.get('podrazdelenie')
    if podrazdelenie_id:
        sotrudniki = sotrudniki.filter(podrazdelenie_id=podrazdelenie_id)
    
    # Добавляем среднее KPI для каждого сотрудника
    from django.db.models import Avg
    sotrudniki_with_kpi = []
    for sotrudnik in sotrudniki:
        avg_kpi = SotrudnikiZarplaty.objects.filter(sotrudnik=sotrudnik).aggregate(avg_kpi=Avg('kpi'))['avg_kpi']
        sotrudnik.avg_kpi = round(avg_kpi, 2) if avg_kpi else 1.0
        sotrudniki_with_kpi.append(sotrudnik)
    
    return render(request, 'sotrudniki/list.html', {'sotrudniki': sotrudniki_with_kpi})


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
    shablony = None
    if sotrudnik.specialnost and hasattr(sotrudnik.specialnost, 'shablony_dokumentov'):
        shablony = sotrudnik.specialnost.shablony_dokumentov
    else:
        # Используем шаблоны "Подсобный рабочий" по умолчанию
        try:
            default_specialnost = Specialnost.objects.get(nazvanie="Подсобный рабочий")
            if hasattr(default_specialnost, 'shablony_dokumentov'):
                shablony = default_specialnost.shablony_dokumentov
        except Specialnost.DoesNotExist:
            pass
    
    if shablony:
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
    if not protokoly_shablony.exists():
        # Используем шаблоны "Подсобный рабочий" по умолчанию
        try:
            default_specialnost = Specialnost.objects.get(nazvanie="Подсобный рабочий")
            protokoly_shablony = SotrudnikiShablonyProtokolov.objects.filter(specialnost=default_specialnost)
        except Specialnost.DoesNotExist:
            pass
    
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
    if not instruktazhi_shablony.exists():
        # Используем шаблоны "Подсобный рабочий" по умолчанию
        try:
            default_specialnost = Specialnost.objects.get(nazvanie="Подсобный рабочий")
            instruktazhi_shablony = ShablonyInstruktazhej.objects.filter(specialnost=default_specialnost)
        except Specialnost.DoesNotExist:
            pass
    
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
        
        # Если шаблон не найден, используем шаблоны для specialnost_id=5
        if not html_content:
            try:
                from .models import ShablonyDokumentovPoSpecialnosti
                default_shablony = ShablonyDokumentovPoSpecialnosti.objects.get(specialnost_id=5)
                
                if doc_type == 'dolzhnostnaya' and default_shablony.dolzhnostnaya_instrukciya:
                    with open(default_shablony.dolzhnostnaya_instrukciya.path, 'r', encoding='utf-8') as f:
                        html_content = f.read()
                    doc_title = "Должностная инструкция"
                elif doc_type == 'kartochka' and default_shablony.lichnaya_kartochka_rabotnika:
                    with open(default_shablony.lichnaya_kartochka_rabotnika.path, 'r', encoding='utf-8') as f:
                        html_content = f.read()
                    doc_title = "Личная карточка работника"
                elif doc_type == 'siz' and default_shablony.lichnaya_kartochka_siz:
                    with open(default_shablony.lichnaya_kartochka_siz.path, 'r', encoding='utf-8') as f:
                        html_content = f.read()
                    doc_title = "Личная карточка СИЗ"
                elif doc_type == 'riski' and default_shablony.karta_ocenki_riskov:
                    with open(default_shablony.karta_ocenki_riskov.path, 'r', encoding='utf-8') as f:
                        html_content = f.read()
                    doc_title = "Карта оценки рисков"
            except ShablonyDokumentovPoSpecialnosti.DoesNotExist:
                pass
    
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


def document_edit(request, pk, doc_type):
    from .models import DokumentySotrudnika
    from django.template import Template, Context
    from django.utils import translation
    
    sotrudnik = get_object_or_404(Sotrudnik, pk=pk)
    
    if request.method == 'POST':
        # Обработка сохранения изменений
        updated_data = {}
        for key, value in request.POST.items():
            if key.startswith('field_'):
                field_name = key.replace('field_', '')
                updated_data[field_name] = value
        
        # Проверяем, нужно ли сохранять в базу данных
        if request.POST.get('save_to_db') == 'true':
            try:
                from datetime import datetime
                
                # Получаем протокол если он есть (для страниц редактирования протоколов)
                protokol_obj = None
                if doc_type == 'protokol':
                    protokol_id = request.GET.get('id')
                    if protokol_id:
                        protokol_obj = get_object_or_404(ProtokolyObucheniya.objects.select_related('shablon_protokola'), 
                                                       id=protokol_id, sotrudnik=sotrudnik)
                
                # Сохраняем изменения в сотрудника
                for field_name, value in updated_data.items():
                    if field_name.startswith('sotrudnik_'):
                        attr_name = field_name.replace('sotrudnik_', '')
                        if hasattr(sotrudnik, attr_name):
                            if 'data_' in attr_name and value:
                                # Преобразуем дату
                                try:
                                    date_value = datetime.strptime(value, '%Y-%m-%d').date()
                                    setattr(sotrudnik, attr_name, date_value)
                                except ValueError:
                                    pass
                            elif attr_name == 'specialnost' and value:
                                # Находим объект специальности по названию
                                try:
                                    specialnost = Specialnost.objects.get(nazvanie=value)
                                    setattr(sotrudnik, attr_name, specialnost)
                                except Specialnost.DoesNotExist:
                                    pass
                            else:
                                setattr(sotrudnik, attr_name, value)
                
                # Сохраняем изменения в протоколе
                if protokol_obj:
                    for field_name, value in updated_data.items():
                        if field_name.startswith('protokol_'):
                            attr_name = field_name.replace('protokol_', '')
                            if hasattr(protokol_obj, attr_name):
                                if 'data_' in attr_name and value:
                                    try:
                                        date_value = datetime.strptime(value, '%Y-%m-%d').date()
                                        setattr(protokol_obj, attr_name, date_value)
                                    except ValueError:
                                        pass
                                else:
                                    setattr(protokol_obj, attr_name, value)
                    protokol_obj.save()
                
                sotrudnik.save()
                return JsonResponse({'success': True, 'message': 'Изменения сохранены в базе данных'})
            except Exception as e:
                return JsonResponse({'success': False, 'message': f'Ошибка: {str(e)}'})
        
        return JsonResponse({'success': True, 'message': 'Изменения сохранены'})
    
    # Получаем HTML содержимое документа
    html_content = ""
    doc_title = ""
    protokol = None
    instruktazh = None
    
    if doc_type == 'instruktazh':
        instruktazh_id = request.GET.get('id')
        if instruktazh_id:
            instruktazh = get_object_or_404(Instruktazhi.objects.select_related('instruktazh'), 
                                          id=instruktazh_id, sotrudnik=sotrudnik)
            if instruktazh.instruktazh.html_file:
                with open(instruktazh.instruktazh.html_file.path, 'r', encoding='utf-8') as f:
                    html_content = f.read()
                doc_title = f"Инструктаж: {instruktazh.instruktazh.get_tip_instruktazha_display()}"
    elif doc_type == 'protokol':
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
    
    # Рендерим HTML с использованием Django Template
    if html_content:
        try:
            translation.activate('ru')
            template = Template(html_content)
            context = Context({
                'sotrudnik': sotrudnik,
                'protokol': protokol,
                'instruktazh': instruktazh
            })
            html_content = template.render(context)
        except Exception as e:
            pass
    
    # Извлекаем поля для редактирования
    import re
    template_fields = re.findall(r'{{\s*([^}]+)\s*}}', html_content)
    editable_fields = []
    
    # Добавляем базовые поля сотрудника
    editable_fields.extend([
        {'name': 'sotrudnik_fio', 'label': 'ФИО', 'value': sotrudnik.fio},
        {
            'name': 'sotrudnik_data_rozhdeniya', 
            'label': 'Дата рождения', 
            'value': sotrudnik.data_rozhdeniya.strftime('%d.%m.%Y') if sotrudnik.data_rozhdeniya else '',
            'date_value': sotrudnik.data_rozhdeniya.strftime('%Y-%m-%d') if sotrudnik.data_rozhdeniya else ''
        },
        {
            'name': 'sotrudnik_data_priema', 
            'label': 'Дата приема', 
            'value': sotrudnik.data_priema.strftime('%d.%m.%Y') if sotrudnik.data_priema else '',
            'date_value': sotrudnik.data_priema.strftime('%Y-%m-%d') if sotrudnik.data_priema else ''
        },
        {
            'name': 'sotrudnik_data_nachala_raboty', 
            'label': 'Дата начала работы', 
            'value': sotrudnik.data_nachala_raboty.strftime('%d.%m.%Y') if sotrudnik.data_nachala_raboty else '',
            'date_value': sotrudnik.data_nachala_raboty.strftime('%Y-%m-%d') if sotrudnik.data_nachala_raboty else ''
        },
    ])
    
    # Добавляем поля протокола если он есть
    if protokol:
        editable_fields.extend([
            {'name': 'protokol_nomer_programmy', 'label': '№ программы', 'value': str(protokol.nomer_programmy)},
            {
                'name': 'protokol_data_prikaza', 
                'label': 'Дата приказа', 
                'value': protokol.data_prikaza.strftime('%d.%m.%Y') if protokol.data_prikaza else '',
                'date_value': protokol.data_prikaza.strftime('%Y-%m-%d') if protokol.data_prikaza else ''
            },
            {
                'name': 'protokol_data_dopuska', 
                'label': 'Дата допуска', 
                'value': protokol.data_dopuska.strftime('%d.%m.%Y') if protokol.data_dopuska else '',
                'date_value': protokol.data_dopuska.strftime('%Y-%m-%d') if protokol.data_dopuska else ''
            },
            {'name': 'protokol_registracionnyy_nomer', 'label': 'Рег. №', 'value': str(protokol.registracionnyy_nomer)},
        ])
    
    for field in template_fields:
        field_clean = field.strip()
        
        # Обрабатываем все поля sotrudnik.*
        if field_clean.startswith('sotrudnik.'):
            field_name = field_clean.split('.')[-1].split('|')[0]
            field_label = field_name.replace('_', ' ').title()
            
            if hasattr(sotrudnik, field_name):
                field_value = getattr(sotrudnik, field_name, '')
                current_value = str(field_value) if field_value else ''
                
                # Обработка дат
                field_data = {
                    'name': f'sotrudnik_{field_name}',
                    'label': f'Сотрудник: {field_label}',
                    'value': current_value
                }
                
                # Если это поле даты, добавляем date_value
                if 'data_' in field_name and hasattr(field_value, 'strftime'):
                    field_data['date_value'] = field_value.strftime('%Y-%m-%d')
                    field_data['value'] = field_value.strftime('%d.%m.%Y')
                
                editable_fields.append(field_data)
            else:
                editable_fields.append({
                    'name': f'sotrudnik_{field_name}',
                    'label': f'Сотрудник: {field_label}',
                    'value': ''
                })
        
        # Обрабатываем поля protokol.*
        elif field_clean.startswith('protokol.') and protokol:
            field_name = field_clean.split('.')[-1].split('|')[0]
            field_label = field_name.replace('_', ' ').title()
            
            if hasattr(protokol, field_name):
                field_value = getattr(protokol, field_name, '')
                current_value = str(field_value) if field_value else ''
                
                # Обработка дат
                field_data = {
                    'name': f'protokol_{field_name}',
                    'label': f'Протокол: {field_label}',
                    'value': current_value
                }
                
                # Если это поле даты, добавляем date_value
                if 'data_' in field_name and hasattr(field_value, 'strftime'):
                    field_data['date_value'] = field_value.strftime('%Y-%m-%d')
                    field_data['value'] = field_value.strftime('%d.%m.%Y')
                
                editable_fields.append(field_data)
            else:
                editable_fields.append({
                    'name': f'protokol_{field_name}',
                    'label': f'Протокол: {field_label}',
                    'value': ''
                })
        
        # Обрабатываем поля instruktazh.*
        elif field_clean.startswith('instruktazh.') and instruktazh:
            field_name = field_clean.split('.')[-1].split('|')[0]
            field_label = field_name.replace('_', ' ').title()
            
            if hasattr(instruktazh, field_name):
                field_value = getattr(instruktazh, field_name, '')
                current_value = str(field_value) if field_value else ''
                
                # Обработка дат
                field_data = {
                    'name': f'instruktazh_{field_name}',
                    'label': f'Инструктаж: {field_label}',
                    'value': current_value
                }
                
                # Если это поле даты, добавляем date_value
                if 'data_' in field_name and hasattr(field_value, 'strftime'):
                    field_data['date_value'] = field_value.strftime('%Y-%m-%d')
                    field_data['value'] = field_value.strftime('%d.%m.%Y')
                
                editable_fields.append(field_data)
            else:
                editable_fields.append({
                    'name': f'instruktazh_{field_name}',
                    'label': f'Инструктаж: {field_label}',
                    'value': ''
                })
    
    context = {
        'sotrudnik': sotrudnik,
        'doc_type': doc_type,
        'doc_title': doc_title,
        'html_content': html_content,
        'editable_fields': editable_fields,
    }
    return render(request, 'sotrudniki/document_edit.html', context)


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
    from object.models import UserProfile, Objekt
    
    if request.user.is_authenticated:
        try:
            user_profile = UserProfile.objects.get(user=request.user)
            organizacii = user_profile.organizations.filter(is_active=True)
        except UserProfile.DoesNotExist:
            organizacii = Organizaciya.objects.none()
    else:
        # Для неавторизованных пользователей показываем демо-организации
        organizacii = Organizaciya.objects.filter(demo=True, is_active=True)
        
        # Добавляем подразделение с id=3 к каждой организации
        for org in organizacii:
            if not org.podrazdeleniya.filter(id=3).exists():
                from .models import OrganizaciyaPodrazdelenie
                OrganizaciyaPodrazdelenie.objects.get_or_create(
                    organizaciya=org,
                    podrazdelenie_id=3
                )
    
    return render(request, 'sotrudniki/organizations.html', {'organizacii': organizacii})


def delete_organization(request, pk):
    from django.http import JsonResponse
    import json
    
    if request.method == 'POST':
        try:
            organizaciya = get_object_or_404(Organizaciya, pk=pk)
            organizaciya.is_active = False
            organizaciya.save()
            return JsonResponse({'success': True})
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)})
    
    return JsonResponse({'success': False, 'error': 'Invalid request method'})





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
    
    if request.user.is_authenticated:
        from object.models import UserProfile
        user_profile, created = UserProfile.objects.get_or_create(user=request.user)
        organizacii = user_profile.organizations.filter(is_active=True)
    else:
        organizacii = Organizaciya.objects.filter(demo=True, is_active=True)
    
    podrazdeleniya = Podrazdelenie.objects.all()
    specialnosti = Specialnost.objects.all()
    
    return render(request, 'sotrudniki/add.html', {
        'organizacii': organizacii,
        'podrazdeleniya': podrazdeleniya,
        'specialnosti': specialnosti,
        'selected_podrazdelenie': podrazdelenie
    })

def sotrudnik_salary(request, sotrudnik_id):
    sotrudnik = get_object_or_404(Sotrudnik, id=sotrudnik_id)
    
    # Генерируем 30 дней от сегодня до минус 30 дней
    end_date = datetime.now().date()
    start_date = end_date - timedelta(days=29)
    
    # Получаем существующие данные о зарплате
    zarplaty_dict = {}
    zarplaty = SotrudnikiZarplaty.objects.filter(
        sotrudnik=sotrudnik,
        data__gte=start_date,
        data__lte=end_date
    ).select_related('objekt')
    
    for zp in zarplaty:
        zarplaty_dict[zp.data] = zp
    
    # Генерируем 30 дней данных (от сегодня к прошлому)
    days_data = []
    for i in range(30):
        current_date = end_date - timedelta(days=i)
        
        if current_date in zarplaty_dict:
            zp = zarplaty_dict[current_date]
            
            # Получаем ставку из базы данных
            from object.models import ResursyPoObjektu, Resurs
            stavka = None
            
            if sotrudnik.specialnost and zp.objekt:
                resurs = Resurs.objects.filter(
                    naimenovanie__icontains=sotrudnik.specialnost.nazvanie,
                    edinica_izmereniya='час'
                ).first()
                
                if resurs:
                    resurs_po_objektu = ResursyPoObjektu.objects.filter(
                        objekt=zp.objekt,
                        resurs=resurs
                    ).first()
                    
                    if resurs_po_objektu:
                        stavka = int(resurs_po_objektu.cena)
            
            # Рассчитываем сумму
            summa = 0
            if stavka and zp.kolichestvo_chasov:
                summa = float(zp.kolichestvo_chasov) * float(zp.kpi) * stavka
            
            days_data.append({
                'date': current_date,
                'objekt_name': zp.objekt.nazvanie,
                'objekt_id': zp.objekt.id,
                'kolichestvo_chasov': zp.kolichestvo_chasov,
                'stavka': int(stavka) if stavka else None,
                'kpi': zp.kpi,
                'summa': int(summa),
                'vydano': zp.vydano
            })
        else:
            days_data.append({
                'date': current_date,
                'objekt_name': None,
                'objekt_id': None,
                'kolichestvo_chasov': 0,
                'stavka': None,
                'kpi': 1.0,
                'summa': 0,
                'vydano': False
            })
    
    # Получаем список объектов для авторизованного пользователя или демо-объекты для неавторизованных
    from object.models import Objekt
    if request.user.is_authenticated:
        from object.models import UserProfile
        from django.db.models import Q
        user_profile, created = UserProfile.objects.get_or_create(user=request.user)
        user_organizations = user_profile.organizations.all()
        objekty = Objekt.objects.filter(
            Q(organizacii__in=user_organizations) | Q(otvetstvennyj__icontains=request.user.get_full_name()),
            is_active=True
        ).distinct()
    else:
        objekty = Objekt.objects.filter(demo=True, is_active=True)
    
    # Рассчитываем выданную сумму
    vydano_sum = 0
    for day_data in days_data:
        if day_data.get('vydano') and day_data.get('summa'):
            vydano_sum += day_data['summa']
    
    context = {
        'sotrudnik': sotrudnik,
        'days_data': days_data,
        'objekty': objekty,
        'start_date': start_date,
        'end_date': end_date,
        'vydano_sum': vydano_sum,
    }
    
    return render(request, 'sotrudniki/salary_detail.html', context)


def get_stavka(request, objekt_id, sotrudnik_id):
    from object.models import ResursyPoObjektu, Resurs
    from django.http import JsonResponse
    
    try:
        sotrudnik = get_object_or_404(Sotrudnik, id=sotrudnik_id)
        
        # Получаем ставку по специальности сотрудника
        if sotrudnik.specialnost:
            resurs = Resurs.objects.filter(
                naimenovanie__icontains=sotrudnik.specialnost.nazvanie,
                edinica_izmereniya='час'
            ).first()
            
            if resurs:
                resurs_po_objektu = ResursyPoObjektu.objects.filter(
                    objekt_id=objekt_id,
                    resurs=resurs
                ).first()
                
                if resurs_po_objektu:
                    return JsonResponse({'stavka': int(resurs_po_objektu.cena)})
        
        return JsonResponse({'stavka': 1000})
    except Exception as e:
        return JsonResponse({'stavka': 1000, 'error': str(e)})


def save_salary(request):
    from django.http import JsonResponse
    import json
    from datetime import datetime
    import logging
    import time
    
    logger = logging.getLogger(__name__)
    
    if request.method == 'POST':
        max_retries = 3
        retry_delay = 0.1
        
        for attempt in range(max_retries):
            try:
                data = json.loads(request.body)
                
                sotrudnik_id = data.get('sotrudnik_id')
                objekt_id = data.get('objekt_id')
                date_str = data.get('date')
                hours = data.get('hours')
                kpi = data.get('kpi')
                
                # Преобразуем дату
                date_obj = datetime.strptime(date_str, '%Y-%m-%d').date()
                
                # Обновляем или создаем запись в таблице SotrudnikiZarplaty
                from object.models import Objekt, Resurs, ResursyPoObjektu, FakticheskijResursPoObjektu, RaskhodResursa
                from sotrudniki.models import Sotrudnik
                
                # Используем update_or_create с уникальными полями для предотвращения дублирования
                zarplata, created = SotrudnikiZarplaty.objects.update_or_create(
                    sotrudnik_id=sotrudnik_id,
                    objekt_id=objekt_id,
                    data=date_obj,
                    defaults={
                        'kolichestvo_chasov': hours,
                        'kpi': kpi
                    }
                )
                
                # Дополнительно записываем данные в таблицу raskhod_resursa
                try:
                    # Получаем сотрудника и объект
                    sotrudnik = Sotrudnik.objects.get(id=sotrudnik_id)
                    objekt = Objekt.objects.get(id=objekt_id)
                    
                    # Ищем ресурс по специальности сотрудника в категории "Кадровое обеспечение"
                    if sotrudnik.specialnost:
                        resurs = Resurs.objects.filter(
                            naimenovanie__icontains=sotrudnik.specialnost.nazvanie,
                            kategoriya_resursa__nazvanie__icontains='Кадровое'
                        ).first()
                        
                        if resurs:
                            # Получаем ресурс по объекту
                            resurs_po_objektu = ResursyPoObjektu.objects.filter(
                                objekt=objekt,
                                resurs=resurs
                            ).first()
                            
                            if resurs_po_objektu:
                                # Получаем фактический ресурс
                                fakticheskij_resurs, _ = FakticheskijResursPoObjektu.objects.get_or_create(
                                    resurs_po_objektu=resurs_po_objektu
                                )
                                
                                # Обновляем запись в таблице RaskhodResursa
                                raskhod, _ = RaskhodResursa.objects.update_or_create(
                                    fakticheskij_resurs=fakticheskij_resurs,
                                    data=date_obj,
                                    defaults={
                                        'izraskhodovano': hours
                                    }
                                )
                                
                                logger.info(f"Данные успешно обновлены в raskhod_resursa: {sotrudnik.fio}, {date_obj}, {hours} часов")
                    
                except Exception as e:
                    logger.error(f"Ошибка при записи в raskhod_resursa: {e}")
                    # Не прерываем выполнение, так как основная запись в SotrudnikiZarplaty уже создана
            
                return JsonResponse({'success': True})
                
            except Exception as e:
                error_msg = str(e)
                if 'database is locked' in error_msg.lower() and attempt < max_retries - 1:
                    time.sleep(retry_delay)
                    retry_delay *= 2
                    continue
                else:
                    logger.error(f"Ошибка сохранения зарплаты: {e}")
                    return JsonResponse({'success': False, 'error': error_msg})
        
        return JsonResponse({'success': False, 'error': 'Database is locked after multiple attempts'})
    
    return JsonResponse({'success': False, 'error': 'Invalid request method'})


def update_vydano(request):
    from django.http import JsonResponse
    import json
    from datetime import datetime
    
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            
            sotrudnik_id = data.get('sotrudnik_id')
            objekt_id = data.get('objekt_id')
            date_str = data.get('date')
            vydano = data.get('vydano')
            
            date_obj = datetime.strptime(date_str, '%Y-%m-%d').date()
            
            zarplata = SotrudnikiZarplaty.objects.filter(
                sotrudnik_id=sotrudnik_id,
                objekt_id=objekt_id,
                data=date_obj
            ).first()
            
            if zarplata:
                zarplata.vydano = vydano
                zarplata.save()
                return JsonResponse({'success': True})
            else:
                return JsonResponse({'success': False, 'error': 'Запись не найдена'})
            
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)})
    
    return JsonResponse({'success': False, 'error': 'Invalid request method'})


def salaries_list(request):
    from datetime import datetime
    from object.models import ResursyPoObjektu, Resurs, UserProfile, Objekt
    from django.db.models import Q
    
    current_date = datetime.now()
    year = request.GET.get('year', str(current_date.year))
    month = request.GET.get('month', str(current_date.month))
    sort_by = request.GET.get('sort', '')
    order = request.GET.get('order', 'desc')
    
    # Фильтруем сотрудников по организациям и объектам пользователя
    if request.user.is_authenticated:
        user_profile, created = UserProfile.objects.get_or_create(user=request.user)
        user_organizations = user_profile.organizations.all()
        user_objects = Objekt.objects.filter(
            Q(organizacii__in=user_organizations) | Q(otvetstvennyj__icontains=request.user.get_full_name()),
            is_active=True
        ).distinct()
        
        sotrudniki_with_salary = Sotrudnik.objects.filter(
            sotrudnikizarplaty__data__year=year,
            sotrudnikizarplaty__data__month=month,
            sotrudnikizarplaty__objekt__in=user_objects
        ).select_related('specialnost').distinct()
    else:
        # Для неавторизованных пользователей показываем сотрудников с демо-объектов и демо-организаций
        from django.db.models import Q
        demo_objects = Objekt.objects.filter(demo=True, is_active=True)
        demo_organizations = Organizaciya.objects.filter(demo=True, is_active=True)
        sotrudniki_with_salary = Sotrudnik.objects.filter(
            Q(sotrudnikizarplaty__objekt__in=demo_objects) | Q(organizaciya__in=demo_organizations),
            sotrudnikizarplaty__data__year=year,
            sotrudnikizarplaty__data__month=month
        ).select_related('specialnost').distinct()
    
    salaries_data = []
    for sotrudnik in sotrudniki_with_salary:
        zarplaty = SotrudnikiZarplaty.objects.filter(
            sotrudnik=sotrudnik,
            data__year=year,
            data__month=month
        ).select_related('objekt')
        
        zarabotano = 0
        vyplacheno = 0
        avg_kpi = 0
        objekty_list = []
        
        for zp in zarplaty:
            stavka = 0
            if sotrudnik.specialnost:
                resurs = Resurs.objects.filter(
                    naimenovanie__icontains=sotrudnik.specialnost.nazvanie,
                    edinica_izmereniya='час'
                ).first()
                
                if resurs:
                    resurs_po_objektu = ResursyPoObjektu.objects.filter(
                        objekt=zp.objekt,
                        resurs=resurs
                    ).first()
                    
                    if resurs_po_objektu:
                        stavka = float(resurs_po_objektu.cena)
            
            summa = float(zp.kolichestvo_chasov) * float(zp.kpi) * stavka
            zarabotano += summa
            avg_kpi += float(zp.kpi)
            
            if zp.objekt.nazvanie not in objekty_list:
                objekty_list.append(zp.objekt.nazvanie)
            
            if zp.vydano:
                vyplacheno += summa
        
        avg_kpi = avg_kpi / len(zarplaty) if zarplaty else 0
        
        salaries_data.append({
            'sotrudnik': sotrudnik,
            'zarabotano': int(zarabotano),
            'vyplacheno': int(vyplacheno),
            'avg_kpi': round(avg_kpi, 1),
            'objekty': ', '.join(objekty_list)
        })
    
    # Сортировка
    if sort_by == 'zarabotano':
        salaries_data.sort(key=lambda x: x['zarabotano'], reverse=(order == 'desc'))
    elif sort_by == 'vyplacheno':
        salaries_data.sort(key=lambda x: x['vyplacheno'], reverse=(order == 'desc'))
    
    # Русские названия месяцев
    month_names_ru = {
        1: 'Январь', 2: 'Февраль', 3: 'Март', 4: 'Апрель',
        5: 'Май', 6: 'Июнь', 7: 'Июль', 8: 'Август',
        9: 'Сентябрь', 10: 'Октябрь', 11: 'Ноябрь', 12: 'Декабрь'
    }
    
    month_int = int(month)
    month_name_ru = month_names_ru.get(month_int, '')
    
    context = {
        'salaries_data': salaries_data,
        'year': year,
        'month': month,
        'month_name': f"{month_name_ru} {year}"
    }
    
    return render(request, 'sotrudniki/salaries_list.html', context)

def control_list(request):
    if request.user.is_authenticated:
        sotrudniki = Sotrudnik.objects.select_related('specialnost').filter(organizaciya__is_active=True)
    else:
        # Для неавторизованных пользователей показываем сотрудников, привязанных к демо-объектам
        from object.models import Objekt
        demo_objects = Objekt.objects.filter(demo=True, is_active=True)
        sotrudniki = Sotrudnik.objects.select_related('specialnost').filter(
            objekty_work__in=demo_objects
        ).distinct()
    
    context = {
        'sotrudniki': sotrudniki
    }
    
    return render(request, 'sotrudniki/control_list.html', context)

def update_control_status(request):
    from django.http import JsonResponse
    import json
    
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            
            sotrudnik_id = data.get('sotrudnik_id')
            field = data.get('field')
            value = data.get('value')
            
            sotrudnik = get_object_or_404(Sotrudnik, id=sotrudnik_id)
            
            if hasattr(sotrudnik, field):
                setattr(sotrudnik, field, value)
                sotrudnik.save()
                return JsonResponse({'success': True})
            else:
                return JsonResponse({'success': False, 'error': 'Поле не найдено'})
            
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)})
    
    return JsonResponse({'success': False, 'error': 'Invalid request method'})
def daily_salaries(request):
    from datetime import datetime
    from object.models import ResursyPoObjektu, Resurs
    from django.db.models import Sum
    
    current_date = datetime.now()
    year = request.GET.get('year', str(current_date.year))
    month = request.GET.get('month', str(current_date.month))
    
    # Русские названия месяцев
    month_names_ru = {
        1: 'Январь', 2: 'Февраль', 3: 'Март', 4: 'Апрель',
        5: 'Май', 6: 'Июнь', 7: 'Июль', 8: 'Август',
        9: 'Сентябрь', 10: 'Октябрь', 11: 'Ноябрь', 12: 'Декабрь'
    }
    
    month_int = int(month)
    month_name_ru = month_names_ru.get(month_int, '')
    
    # Получаем все записи зарплат за период
    zarplaty = SotrudnikiZarplaty.objects.filter(
        data__year=year,
        data__month=month
    ).select_related('sotrudnik', 'objekt').order_by('data', 'sotrudnik__fio')
    
    # Группируем по датам
    grouped_data = {}
    daily_totals = {}
    
    for zp in zarplaty:
        # Получаем ставку
        stavka = 0
        if zp.sotrudnik.specialnost:
            resurs = Resurs.objects.filter(
                naimenovanie__icontains=zp.sotrudnik.specialnost.nazvanie,
                edinica_izmereniya='час'
            ).first()
            
            if resurs:
                resurs_po_objektu = ResursyPoObjektu.objects.filter(
                    objekt=zp.objekt,
                    resurs=resurs
                ).first()
                
                if resurs_po_objektu:
                    stavka = float(resurs_po_objektu.cena)
        
        summa = float(zp.kolichestvo_chasov) * float(zp.kpi) * stavka
        
        # Группируем по датам
        if zp.data not in grouped_data:
            grouped_data[zp.data] = []
            daily_totals[zp.data] = 0
        
        grouped_data[zp.data].append({
            'sotrudnik': zp.sotrudnik.fio,
            'objekt': zp.objekt.nazvanie if zp.objekt else '-',
            'specialnost': zp.sotrudnik.specialnost.nazvanie if zp.sotrudnik.specialnost else '-',
            'kolichestvo_chasov': zp.kolichestvo_chasov,
            'stavka': int(stavka),
            'kpi': zp.kpi,
            'summa': int(summa)
        })
        
        daily_totals[zp.data] += int(summa)
    
    # Преобразуем в список для шаблона
    daily_data = []
    for date in sorted(grouped_data.keys(), reverse=True):
        for i, item in enumerate(grouped_data[date]):
            daily_data.append({
                'data': date,
                'is_first_in_group': i == 0,
                'group_size': len(grouped_data[date]),
                'sotrudnik': item['sotrudnik'],
                'objekt': item['objekt'],
                'specialnost': item['specialnost'],
                'kolichestvo_chasov': item['kolichestvo_chasov'],
                'stavka': item['stavka'],
                'kpi': item['kpi'],
                'summa': item['summa'],
                'daily_total': daily_totals[date]
            })
    
    context = {
        'daily_data': daily_data,
        'year': year,
        'month': month,
        'month_name': f"{month_name_ru} {year}"
    }
    
    return render(request, 'sotrudniki/daily_salaries.html', context)

@login_required
def delete_sotrudnik(request, pk):
    """Удаление привязки сотрудника к объектам пользователя"""
    sotrudnik = get_object_or_404(Sotrudnik, pk=pk)
    
    # Получаем объекты пользователя
    from object.models import UserProfile, Objekt
    from django.db.models import Q
    user_profile, created = UserProfile.objects.get_or_create(user=request.user)
    user_organizations = user_profile.organizations.all()
    user_objects = Objekt.objects.filter(
        Q(organizacii__in=user_organizations) | Q(otvetstvennyj__icontains=request.user.get_full_name()),
        is_active=True
    ).distinct()
    
    # Удаляем привязку сотрудника к объектам пользователя
    sotrudnik.objekty_work.remove(*user_objects)
    
    from django.contrib import messages
    messages.success(request, f'Привязка сотрудника {sotrudnik.fio} к вашим объектам удалена')
    
    podrazdelenie_id = request.GET.get('podrazdelenie')
    if podrazdelenie_id:
        return redirect(f'/sotrudniki/?podrazdelenie={podrazdelenie_id}')
    return redirect('sotrudniki:list')