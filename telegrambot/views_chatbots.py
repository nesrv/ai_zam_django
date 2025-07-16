from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse
from object.models import Objekt
import json
from .models import ChatMessage

async def get_chat_messages(chat_id, bot_token):
    """Получение последних сообщений из чата"""
    try:
        bot = Bot(token=bot_token)
        # Получаем последние 10 сообщений
        updates = await bot.get_updates(limit=10)
        messages = []
        
        for update in updates:
            if update.message and str(update.message.chat.id) == str(chat_id):
                messages.append({
                    'text': update.message.text or 'Медиа сообщение',
                    'date': update.message.date.strftime('%H:%M %d.%m'),
                    'from_user': update.message.from_user.first_name if update.message.from_user else 'Неизвестно'
                })
        
        await bot.session.close()
        return messages[-10:]  # Последние 10
    except Exception as e:
        return []

def chatbots_page(request):
    """Страница чат-ботов для объектов"""
    objekty = Objekt.objects.filter(is_active=True)
    
    # Получаем сообщения для объектов с chat_id
    for objekt in objekty:
        if objekt.chat_id:
            messages = ChatMessage.objects.filter(chat_id=objekt.chat_id)[:10]
            objekt.recent_messages = [
                {
                    'text': msg.message_text,
                    'from_user': msg.from_user,
                    'date': msg.created_at.strftime('%H:%M %d.%m')
                }
                for msg in messages
            ]
        else:
            objekt.recent_messages = []
    
    context = {
        'objekty': objekty
    }
    
    return render(request, 'telegrambot/chatbots.html', context)

def update_chat_id(request):
    """Обновление chat_id для объекта"""
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            objekt_id = data.get('objekt_id')
            chat_id = data.get('chat_id')
            
            objekt = get_object_or_404(Objekt, id=objekt_id)
            objekt.chat_id = chat_id
            objekt.save()
            
            return JsonResponse({'success': True})
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)})
    
    return JsonResponse({'success': False, 'error': 'Invalid request method'})