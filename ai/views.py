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
import os
from datetime import datetime
import markdown

# Create your views here.




def index(request):
    """Главная страница AI приложения с информацией о подключении"""
    # Проверяем наличие API ключа
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
@require_http_methods(["POST"])
def home_chat_api(request):
    """API для чат-бота на главной странице"""
    try:
        data = json.loads(request.body)
        message = data.get('message', '').strip()
        
        if not message:
            return JsonResponse({'error': 'Сообщение не может быть пустым'}, status=400)
        
        # Создаем временную сессию для главной страницы
        session = ChatSession.objects.create(session_id=str(uuid.uuid4())[:8])
        
        # Сохраняем сообщение пользователя
        ChatMessage.objects.create(
            session=session,
            message_type='user',
            content=message
        )
        
        # Получаем ответ от DeepSeek
        try:
            response_text = get_ai_response(message, [])
        except Exception as e:
            # Если API недоступен, используем запасные ответы
            fallback_responses = [
                "Спасибо за ваш вопрос! Я проанализирую его и дам подробный ответ.",
                "Отличный вопрос! Позвольте мне составить для вас детальный план.",
                "Понимаю вашу задачу. Сейчас подготовлю необходимую документацию.",
                "Интересная задача! Давайте разберем её по пунктам.",
                "Спасибо! Я изучу ваш запрос и предоставлю профессиональную консультацию."
            ]
            response_text = fallback_responses[hash(message) % len(fallback_responses)]
        
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

@csrf_exempt
@require_http_methods(["POST"])
def generate_document(request):
    """Генерация документа на основе ответа чат-бота"""
    try:
        print(f"DEBUG: Content-Type: {request.content_type}")
        print(f"DEBUG: Request body length: {len(request.body) if request.body else 0}")
        print(f"DEBUG: POST data: {request.POST}")
        
        # Пытаемся получить данные из JSON
        try:
            data = json.loads(request.body)
            content = data.get('content', '').strip()
            doc_type = data.get('type', 'txt')
            filename = data.get('filename', 'document')
            print(f"DEBUG: JSON data - content length: {len(content)}, type: {doc_type}, filename: {filename}")
        except (json.JSONDecodeError, AttributeError) as e:
            print(f"DEBUG: JSON decode error: {e}")
            # Если JSON не работает, берем из form data
            content = request.POST.get('content', '').strip()
            doc_type = request.POST.get('type', 'txt')
            filename = request.POST.get('filename', 'document')
            print(f"DEBUG: Form data - content length: {len(content)}, type: {doc_type}, filename: {filename}")
        
        if not content:
            print("DEBUG: Empty content")
            return JsonResponse({'error': 'Содержимое документа не может быть пустым'}, status=400)
        
        # Очищаем имя файла от недопустимых символов
        filename = "".join(c for c in filename if c.isalnum() or c in (' ', '-', '_')).rstrip()
        if not filename:
            filename = 'document'
        
        print(f"DEBUG: Processing document - type: {doc_type}, filename: {filename}")
        
        # Добавляем временную метку
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        if doc_type == 'txt':
            # Генерируем текстовый файл
            response = HttpResponse(content, content_type='text/plain; charset=utf-8')
            response['Content-Disposition'] = f'attachment; filename="{filename}_{timestamp}.txt"'
            print(f"DEBUG: Generated TXT file: {filename}_{timestamp}.txt")
            return response
            
        elif doc_type == 'md':
            # Генерируем Markdown файл
            response = HttpResponse(content, content_type='text/markdown; charset=utf-8')
            response['Content-Disposition'] = f'attachment; filename="{filename}_{timestamp}.md"'
            print(f"DEBUG: Generated MD file: {filename}_{timestamp}.md")
            return response
            
        elif doc_type == 'pdf':
            # Конвертируем Markdown в HTML для PDF
            html_content = markdown.markdown(content, extensions=['tables', 'fenced_code', 'codehilite'])
            
            full_html = f"""
            <!DOCTYPE html>
            <html>
            <head>
                <meta charset="utf-8">
                <title>{filename}</title>
                <style>
                    body {{
                        font-family: Arial, sans-serif;
                        margin: 40px;
                        line-height: 1.6;
                        color: #333;
                    }}
                    .header {{
                        border-bottom: 2px solid #007AFF;
                        padding-bottom: 10px;
                        margin-bottom: 20px;
                    }}
                    .content {{
                        font-size: 14px;
                    }}
                    .footer {{
                        margin-top: 30px;
                        padding-top: 10px;
                        border-top: 1px solid #ddd;
                        font-size: 12px;
                        color: #666;
                    }}
                    /* Стили для Markdown */
                    h1, h2, h3, h4, h5, h6 {{
                        color: #007AFF;
                        margin-top: 20px;
                        margin-bottom: 10px;
                    }}
                    code {{
                        background: #f4f4f4;
                        padding: 2px 4px;
                        border-radius: 3px;
                        font-family: 'Courier New', monospace;
                    }}
                    pre {{
                        background: #f8f8f8;
                        padding: 15px;
                        border-radius: 5px;
                        overflow-x: auto;
                        border-left: 4px solid #007AFF;
                    }}
                    blockquote {{
                        border-left: 4px solid #007AFF;
                        margin: 0;
                        padding-left: 15px;
                        color: #666;
                        font-style: italic;
                    }}
                    table {{
                        border-collapse: collapse;
                        width: 100%;
                        margin: 15px 0;
                    }}
                    th, td {{
                        border: 1px solid #ddd;
                        padding: 8px;
                        text-align: left;
                    }}
                    th {{
                        background-color: #f2f2f2;
                        font-weight: bold;
                    }}
                    ul, ol {{
                        padding-left: 20px;
                    }}
                    li {{
                        margin: 5px 0;
                    }}
                </style>
            </head>
            <body>
                <div class="header">
                    <h1>{filename}</h1>
                    <p>Сгенерировано: {datetime.now().strftime("%d.%m.%Y %H:%M")}</p>
                </div>
                <div class="content">{html_content}</div>
                <div class="footer">
                    <p>Документ создан с помощью AI-Зам</p>
                </div>
            </body>
            </html>
            """
            
            response = HttpResponse(full_html, content_type='text/html; charset=utf-8')
            response['Content-Disposition'] = f'attachment; filename="{filename}_{timestamp}.html"'
            print(f"DEBUG: Generated HTML file: {filename}_{timestamp}.html")
            return response
            
        elif doc_type == 'docx':
            # Конвертируем Markdown в HTML для DOCX
            html_content = markdown.markdown(content, extensions=['tables', 'fenced_code', 'codehilite'])
            
            full_html = f"""
            <!DOCTYPE html>
            <html>
            <head>
                <meta charset="utf-8">
                <title>{filename}</title>
                <style>
                    body {{
                        font-family: 'Times New Roman', serif;
                        margin: 40px;
                        line-height: 1.5;
                        color: #000;
                    }}
                    .header {{
                        text-align: center;
                        margin-bottom: 30px;
                    }}
                    .content {{
                        font-size: 14px;
                        text-align: justify;
                    }}
                    /* Стили для Markdown */
                    h1, h2, h3, h4, h5, h6 {{
                        color: #000;
                        margin-top: 20px;
                        margin-bottom: 10px;
                    }}
                    code {{
                        background: #f4f4f4;
                        padding: 2px 4px;
                        border-radius: 3px;
                        font-family: 'Courier New', monospace;
                    }}
                    pre {{
                        background: #f8f8f8;
                        padding: 15px;
                        border-radius: 5px;
                        overflow-x: auto;
                        border-left: 4px solid #000;
                    }}
                    blockquote {{
                        border-left: 4px solid #000;
                        margin: 0;
                        padding-left: 15px;
                        color: #333;
                        font-style: italic;
                    }}
                    table {{
                        border-collapse: collapse;
                        width: 100%;
                        margin: 15px 0;
                    }}
                    th, td {{
                        border: 1px solid #000;
                        padding: 8px;
                        text-align: left;
                    }}
                    th {{
                        background-color: #f2f2f2;
                        font-weight: bold;
                    }}
                    ul, ol {{
                        padding-left: 20px;
                    }}
                    li {{
                        margin: 5px 0;
                    }}
                </style>
            </head>
            <body>
                <div class="header">
                    <h1>{filename}</h1>
                </div>
                <div class="content">{html_content}</div>
            </body>
            </html>
            """
            
            response = HttpResponse(full_html, content_type='text/html; charset=utf-8')
            response['Content-Disposition'] = f'attachment; filename="{filename}_{timestamp}.html"'
            print(f"DEBUG: Generated DOCX file: {filename}_{timestamp}.html")
            return response
            
        else:
            print(f"DEBUG: Unsupported document type: {doc_type}")
            return JsonResponse({'error': 'Неподдерживаемый тип документа'}, status=400)
            
    except Exception as e:
        print(f"DEBUG: Exception in generate_document: {e}")
        return JsonResponse({'error': f'Ошибка сервера: {str(e)}'}, status=500)
