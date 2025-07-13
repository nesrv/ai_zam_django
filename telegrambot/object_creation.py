"""
Функции для создания объектов из JSON данных AI-агента
"""
import json
import os
import uuid
from datetime import date, timedelta
from django.core.files.base import ContentFile
from django.core.files.storage import default_storage
from django.utils import timezone
from django.conf import settings

def save_json_and_create_object(json_data):
    """
    Сохраняет JSON в файл, записывает в ai_chatmessage и создает объект в БД
    """
    from object.models import Objekt, KategoriyaResursa, Resurs, ResursyPoObjektu, FakticheskijResursPoObjektu
    from sotrudniki.models import Specialnost, Podrazdelenie, Sotrudnik
    from ai.models import ChatSession, ChatMessage
    
    # Сохраняем JSON в файл
    filename = f"ai_object_{timezone.now().strftime('%Y%m%d_%H%M%S')}_{uuid.uuid4().hex[:8]}.json"
    file_path = f'documents_ai/{filename}'
    media_dir = os.path.join(settings.MEDIA_ROOT, 'documents_ai')
    os.makedirs(media_dir, exist_ok=True)
    saved_path = default_storage.save(file_path, ContentFile(json.dumps(json_data, ensure_ascii=False, indent=2).encode('utf-8')))
    
    # Сохраняем в ai_chatmessage
    session, _ = ChatSession.objects.get_or_create(session_id='telegram_object_creation')
    ChatMessage.objects.create(session=session, message_type='assistant', content='JSON для создания объекта', file=saved_path)
    
    # Создаем объект
    obj = Objekt.objects.create(
        nazvanie=json_data.get('nazvanie', 'Объект из AI'),
        data_nachala=date.today(),
        data_plan_zaversheniya=date.today() + timedelta(days=365),
        otvetstvennyj='AI Администратор'
    )
    
    podrazdelenie, _ = Podrazdelenie.objects.get_or_create(kod='792', defaults={'nazvanie': 'Линейные сотрудники'})
    
    # Обрабатываем kategoriya_resursa
    if 'kategoriya_resursa' in json_data:
        for category_name, items in json_data['kategoriya_resursa'].items():
            category, _ = KategoriyaResursa.objects.get_or_create(nazvanie=category_name, defaults={'raskhod_dokhod': True})
            
            for item in items:
                resource_name = item.get('наименование') or item.get('sotrudniki_specialnost', 'Не указано')
                quantity = item.get('количество') or item.get('часов', 1)
                price = item.get('цена_за_ед') or item.get('стоимость_часа', 0)
                unit = item.get('ед_изм', 'шт')
                
                resource, _ = Resurs.objects.get_or_create(naimenovanie=resource_name, kategoriya_resursa=category, defaults={'edinica_izmereniya': unit})
                
                if category_name == 'Кадровое обеспечение':
                    specialnost, _ = Specialnost.objects.get_or_create(nazvanie=resource_name, defaults={'kategoriya': 'Строительство'})
                    sotrudnik, _ = Sotrudnik.objects.get_or_create(
                        fio=f'{resource_name} (AI)', data_rozhdeniya=date(1990, 1, 1), data_priema=date.today(), data_nachala_raboty=date.today(),
                        defaults={'specialnost': specialnost, 'podrazdelenie': podrazdelenie}
                    )
                    obj.sotrudniki.add(sotrudnik)
                
                resurs_po_objektu = ResursyPoObjektu.objects.create(objekt=obj, resurs=resource, kolichestvo=quantity, cena=price)
                FakticheskijResursPoObjektu.objects.create(resurs_po_objektu=resurs_po_objektu)
    
    # Обрабатываем works
    if 'works' in json_data:
        for work_section in json_data['works']:
            section_name = work_section.get('section', 'Работы')
            category, _ = KategoriyaResursa.objects.get_or_create(nazvanie=section_name, defaults={'raskhod_dokhod': False})
            
            for item in work_section.get('items', []):
                resource_name = item.get('наименование', 'Не указано')
                quantity = item.get('количество', 1)
                unit = item.get('ед_изм', 'шт')
                
                resource, _ = Resurs.objects.get_or_create(naimenovanie=resource_name, kategoriya_resursa=category, defaults={'edinica_izmereniya': unit})
                resurs_po_objektu = ResursyPoObjektu.objects.create(objekt=obj, resurs=resource, kolichestvo=quantity, cena=1000)
                FakticheskijResursPoObjektu.objects.create(resurs_po_objektu=resurs_po_objektu)
    
    return {
        'ok': True,
        'object_id': obj.id,
        'object_name': obj.nazvanie,
        'file_path': saved_path,
        'message': 'Объект успешно создан в базе данных'
    }