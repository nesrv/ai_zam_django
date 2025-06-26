import uuid
import json
from django.shortcuts import render
from django.http import HttpResponse, JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from .models import ChatSession, ChatMessage
from .services import (
    generate_weekly_menu, 
    generate_daily_menu, 
    format_menu_text,
    get_ai_response
)

# Create your views here.




def index(request):
    """Главная страница AI приложения с информацией о подключении"""
    # Проверяем наличие API ключа
    import os
    from dotenv import load_dotenv
    load_dotenv()
    
    deepseek_api_key = os.getenv('DEEPSEEK_API_KEY')
    api_status = "✅ Настроен" if deepseek_api_key else "❌ Не настроен"
    
    context = {
        'api_status': api_status,
        'api_key_preview': deepseek_api_key[:20] + "..." if deepseek_api_key else "Не указан",
        'deepseek_url': "https://api.deepseek.com",
    }
    
    return render(request, 'ai/index.html', context)

@csrf_exempt
@require_http_methods(["POST"])
def chat_api(request):
    """API для чат-бота"""
    try:
        data = json.loads(request.body)
        message = data.get('message', '').strip()
        session_id = data.get('session_id')
        chat_type = data.get('type', 'general')  # general, daily_menu, weekly_menu
        
        if not message:
            return JsonResponse({'error': 'Сообщение не может быть пустым'}, status=400)
        
        # Получаем или создаем сессию
        session = None
        if session_id:
            try:
                session = ChatSession.objects.get(session_id=session_id, is_active=True)
            except ChatSession.DoesNotExist:
                session = None
        
        if not session:
            session = ChatSession.objects.create(session_id=str(uuid.uuid4())[:8])
        
        # Сохраняем сообщение пользователя
        ChatMessage.objects.create(
            session=session,
            message_type='user',
            content=message
        )
        
        # Генерируем ответ в зависимости от типа чата
        if chat_type == 'daily_menu':
            response_text = generate_daily_menu(message)
            response_text = format_menu_text(response_text)
        elif chat_type == 'weekly_menu':
            response_text = generate_weekly_menu(message)
            response_text = format_menu_text(response_text)
        else:
            # Общий чат - получаем историю сообщений
            session_messages = session.messages.all()
            response_text = get_ai_response(message, session_messages)
        
        # Сохраняем ответ AI
        ChatMessage.objects.create(
            session=session,
            message_type='assistant',
            content=response_text
        )
        
        return JsonResponse({
            'response': response_text,
            'session_id': session.session_id
        })
        
    except json.JSONDecodeError:
        return JsonResponse({'error': 'Неверный формат JSON'}, status=400)
    except Exception as e:
        return JsonResponse({'error': f'Ошибка сервера: {str(e)}'}, status=500)

@csrf_exempt
@require_http_methods(["GET"])
def chat_history(request):
    """Получение истории чата"""
    session_id = request.GET.get('session_id')
    
    if not session_id:
        return JsonResponse({'error': 'Session ID обязателен'}, status=400)
    
    try:
        session = ChatSession.objects.get(session_id=session_id, is_active=True)
        messages = session.messages.all()
        
        history = []
        for msg in messages:
            history.append({
                'type': msg.message_type,
                'content': msg.content,
                'timestamp': msg.created_at.isoformat()
            })
        
        return JsonResponse({'history': history})
        
    except ChatSession.DoesNotExist:
        return JsonResponse({'error': 'Сессия не найдена'}, status=404)
    except Exception as e:
        return JsonResponse({'error': f'Ошибка сервера: {str(e)}'}, status=500)

def chat_interface(request):
    """Интерфейс чат-бота"""
    return render(request, 'ai/chat.html')

def menu_generator(request):
    """Генератор меню"""
    return render(request, 'ai/menu_generator.html')
