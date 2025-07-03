import json
import logging
from django.http import JsonResponse, FileResponse, HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from django.views.decorators.clickjacking import xframe_options_exempt
from django.shortcuts import render
from django.db.models import Count, Q
from django.utils import timezone
from datetime import timedelta
from .services import process_telegram_update, send_telegram_message, check_bot_token, BOT_TOKEN
from .models import TelegramUser, TelegramMessage
import io
from fpdf import FPDF
from docx import Document
import pandas as pd
from telegrambot.models import TemporaryDocument
import os
from io import BytesIO
from fpdf.errors import FPDFException

logger = logging.getLogger(__name__)

@csrf_exempt
# @require_POST  # временно убираем для теста
def telegram_webhook(request):
    print('=== ВЫЗВАН telegram_webhook ===')
    import logging
    logging.getLogger('django').warning('=== ВЫЗВАН telegram_webhook ===')
    """Webhook для получения сообщений от Telegram"""
    logger.info("=== WEBHOOK ЗАПРОС ===")
    
    try:
        # Логируем базовую информацию о запросе
        logger.info(f"Метод: {request.method}")
        logger.info(f"Content-Type: {request.content_type}")
        logger.info(f"User-Agent: {request.META.get('HTTP_USER_AGENT', 'Не указан')}")
        logger.info(f"Remote IP: {request.META.get('REMOTE_ADDR', 'Неизвестно')}")
        logger.info(f"Размер тела запроса: {len(request.body)} байт")
        
        if request.method != 'POST':
            logger.warning(f"Неверный метод: {request.method}")
            return JsonResponse({'error': 'Method not allowed'}, status=405)
        
        # Проверяем Content-Type
        content_type = request.content_type or ''
        if 'application/json' not in content_type:
            logger.warning(f"Неверный Content-Type: {content_type}")
            return JsonResponse({'error': 'Content-Type must be application/json'}, status=400)
        
        # Проверяем размер тела запроса
        if len(request.body) == 0:
            logger.warning("Пустое тело запроса")
            return JsonResponse({'error': 'Empty request body'}, status=400)
        
        # Проверяем User-Agent
        user_agent = request.META.get('HTTP_USER_AGENT', '')
        remote_addr = request.META.get('REMOTE_ADDR', '')
        
        # Простая проверка IP (можно улучшить с помощью ipaddress модуля)
        if 'TelegramBot' not in user_agent and 'python-telegram-bot' not in user_agent:
            logger.warning(f"Подозрительный запрос к webhook от: {remote_addr} - {user_agent}")
            # Не блокируем, но логируем для безопасности
        
        # Декодируем JSON
        try:
            update_data = json.loads(request.body.decode('utf-8'))
            logger.info(f"Успешно декодирован JSON: {update_data}")
        except json.JSONDecodeError as e:
            logger.error(f"Ошибка декодирования JSON: {e}")
            logger.error(f"Тело запроса: {request.body}")
            return JsonResponse({'error': 'Invalid JSON'}, status=400)
        except Exception as e:
            logger.error(f"Неожиданная ошибка при декодировании JSON: {e}")
            return JsonResponse({'error': 'JSON processing error'}, status=400)
        
        # Проверяем структуру update
        if not isinstance(update_data, dict):
            logger.error(f"Update не является словарем: {type(update_data)}")
            return JsonResponse({'error': 'Invalid update format'}, status=400)
        
        if 'update_id' not in update_data:
            logger.error("Отсутствует update_id в update")
            return JsonResponse({'error': 'Missing update_id'}, status=400)
        
        # Обрабатываем update
        try:
            result = process_telegram_update(update_data)
            logger.info(f"Update обработан успешно: {result}")
            return JsonResponse({'status': 'ok'})
        except Exception as e:
            logger.error(f"Ошибка при обработке update: {e}")
            return JsonResponse({'error': 'Update processing error'}, status=500)
            
    except Exception as e:
        logger.error(f"Критическая ошибка в webhook: {e}")
        logger.error(f"Тип ошибки: {type(e)}")
        import traceback
        logger.error(f"Traceback: {traceback.format_exc()}")
        return JsonResponse({'error': 'Internal server error'}, status=500)

def bot_status(request):
    """Страница статуса бота с чатом"""
    try:
        # Получаем статистику
        total_users = TelegramUser.objects.count()
        active_users = TelegramUser.objects.filter(is_active=True).count()
        total_messages = TelegramMessage.objects.count()
        
        # Получаем все сообщения для чата, отсортированные по времени
        all_messages = TelegramMessage.objects.select_related('user').order_by('created_at')
        
        # Последние сообщения для статистики (первые 10)
        recent_messages = all_messages[:10]
        
        context = {
            'total_users': total_users,
            'active_users': active_users,
            'total_messages': total_messages,
            'recent_messages': recent_messages,
            'all_messages': all_messages,  # Все сообщения для чата
        }
        
        return render(request, 'telegrambot/status.html', context)
        
    except Exception as e:
        logger.error(f"Ошибка получения статуса бота: {e}")
        return JsonResponse({'error': str(e)}, status=500)

def bot_management(request):
    """Страница управления ботом"""
    try:
        # Получаем список пользователей
        users = TelegramUser.objects.order_by('-created_at')[:50]
        
        context = {
            'users': users,
        }
        
        return render(request, 'telegrambot/management.html', context)
        
    except Exception as e:
        logger.error(f"Ошибка управления ботом: {e}")
        return JsonResponse({'error': str(e)}, status=500)

@csrf_exempt
@require_POST
def send_broadcast(request):
    """Отправка массового сообщения всем пользователям"""
    try:
        data = json.loads(request.body)
        message = data.get('message', '').strip()
        
        if not message:
            return JsonResponse({'error': 'Сообщение не может быть пустым'}, status=400)
        
        # Получаем всех активных пользователей
        users = TelegramUser.objects.filter(is_active=True)
        total_users = users.count()
        
        if total_users == 0:
            return JsonResponse({
                'ok': False,
                'error': 'Нет активных пользователей для отправки сообщения',
                'sent_count': 0,
                'total_users': 0
            })
        
        # Проверяем токен бота перед отправкой
        token = BOT_TOKEN
        is_valid, bot_info = check_bot_token(token)
        if not is_valid:
            return JsonResponse({
                'ok': False,
                'error': f'Недействительный токен бота: {bot_info}',
                'sent_count': 0,
                'total_users': total_users
            })
        
        sent_count = 0
        failed_count = 0
        errors = []
        
        for user in users:
            try:
                logger.info(f"Отправка сообщения пользователю {user.telegram_id} ({user.first_name})")
                result = send_telegram_message(user.telegram_id, message)
                
                if result and result.get('ok'):
                    sent_count += 1
                    logger.info(f"✅ Сообщение успешно отправлено пользователю {user.telegram_id}")
                else:
                    failed_count += 1
                    error_msg = f"Ошибка отправки пользователю {user.telegram_id}: {result}"
                    errors.append(error_msg)
                    logger.error(error_msg)
                    
                    # Если пользователь заблокировал бота, помечаем его как неактивного
                    if result and result.get('error_code') == 400:
                        description = result.get('description', '').lower()
                        if 'bot was blocked' in description or 'chat not found' in description:
                            user.is_active = False
                            user.save()
                            logger.info(f"Пользователь {user.telegram_id} помечен как неактивный")
                    
            except Exception as e:
                failed_count += 1
                error_msg = f"Исключение при отправке пользователю {user.telegram_id}: {str(e)}"
                errors.append(error_msg)
                logger.error(error_msg)
        
        logger.info(f"Массовая рассылка завершена: {sent_count}/{total_users} успешно отправлено")
        
        return JsonResponse({
            'ok': True,
            'sent_count': sent_count,
            'failed_count': failed_count,
            'total_users': total_users,
            'errors': errors[:5] if errors else []  # Возвращаем только первые 5 ошибок
        })
        
    except json.JSONDecodeError:
        return JsonResponse({'error': 'Invalid JSON'}, status=400)
    except Exception as e:
        logger.error(f"Общая ошибка массовой рассылки: {e}")
        return JsonResponse({'error': str(e)}, status=500)

def webhook_status(request):
    """Страница статуса webhook для проверки"""
    if request.method == 'GET':
        return JsonResponse({
            'status': 'ok',
            'message': 'Telegram webhook endpoint is working',
            'method': 'GET',
            'note': 'This endpoint accepts only POST requests from Telegram'
        })
    else:
        return JsonResponse({'error': 'Method not allowed'}, status=405)

def bot_dashboard(request):
    """Главная страница с историей и активностью бота"""
    try:
        # Общая статистика
        total_users = TelegramUser.objects.count()
        active_users = TelegramUser.objects.filter(is_active=True).count()
        total_messages = TelegramMessage.objects.count()
        
        # Статистика за последние 7 дней
        week_ago = timezone.now() - timedelta(days=7)
        new_users_week = TelegramUser.objects.filter(created_at__gte=week_ago).count()
        messages_week = TelegramMessage.objects.filter(created_at__gte=week_ago).count()
        
        # Статистика за последние 24 часа
        day_ago = timezone.now() - timedelta(days=1)
        new_users_day = TelegramUser.objects.filter(created_at__gte=day_ago).count()
        messages_day = TelegramMessage.objects.filter(created_at__gte=day_ago).count()
        
        # Последние активные пользователи
        recent_active_users = TelegramUser.objects.filter(
            messages__created_at__gte=day_ago
        ).distinct().order_by('-updated_at')[:10]
        
        # Последние сообщения
        recent_messages = TelegramMessage.objects.select_related('user').order_by('-created_at')[:20]
        
        # Статистика по типам сообщений
        message_types = TelegramMessage.objects.values('message_type').annotate(
            count=Count('id')
        ).order_by('-count')
        
        # Топ пользователей по активности
        top_users = TelegramUser.objects.annotate(
            message_count=Count('messages')
        ).filter(message_count__gt=0).order_by('-message_count')[:10]
        
        # Активность по часам (последние 24 часа)
        hourly_activity = []
        for i in range(24):
            hour_start = timezone.now() - timedelta(hours=23-i)
            hour_end = hour_start + timedelta(hours=1)
            count = TelegramMessage.objects.filter(
                created_at__gte=hour_start,
                created_at__lt=hour_end
            ).count()
            hourly_activity.append({
                'hour': hour_start.hour,
                'count': count
            })
        
        context = {
            # Общая статистика
            'total_users': total_users,
            'active_users': active_users,
            'total_messages': total_messages,
            
            # Статистика за неделю
            'new_users_week': new_users_week,
            'messages_week': messages_week,
            
            # Статистика за день
            'new_users_day': new_users_day,
            'messages_day': messages_day,
            
            # Активность
            'recent_active_users': recent_active_users,
            'recent_messages': recent_messages,
            'message_types': message_types,
            'top_users': top_users,
            'hourly_activity': hourly_activity,
            
            # Статус бота
            'bot_status': 'active',  # Можно добавить реальную проверку статуса
        }
        
        return render(request, 'telegrambot/dashboard.html', context)
        
    except Exception as e:
        logger.error(f"Ошибка получения данных dashboard: {e}")
        return JsonResponse({'error': str(e)}, status=500)

@csrf_exempt
@require_POST
def generate_document(request):
    """Генерация документа с помощью DeepSeek API"""
    try:
        data = json.loads(request.body)
        prompt = data.get('prompt', '').strip()
        
        logger.info(f"Получен запрос на генерацию документа: {prompt}")
        
        if not prompt:
            logger.error("Пустой запрос на генерацию документа")
            return JsonResponse({'error': 'Запрос не может быть пустым'}, status=400)
        
        # Импортируем функцию генерации документа
        from .services import generate_document_with_deepseek
        
        # Генерируем документ с помощью DeepSeek
        logger.info("Отправляю запрос к DeepSeek API...")
        generated_content = generate_document_with_deepseek(prompt)
        logger.info(f"Получен ответ от DeepSeek: {generated_content[:200]}...")
        
        if generated_content.startswith('Ошибка'):
            logger.error(f"Ошибка DeepSeek API: {generated_content}")
            return JsonResponse({
                'ok': False,
                'error': generated_content
            })
        
        # Получаем всех активных пользователей для отправки
        users = TelegramUser.objects.filter(is_active=True)
        total_users = users.count()
        logger.info(f"Найдено активных пользователей: {total_users}")
        
        if total_users == 0:
            logger.warning("Нет активных пользователей для отправки документа")
            return JsonResponse({
                'ok': False,
                'error': 'Нет активных пользователей для отправки документа',
                'generated_content': generated_content
            })
        
        # Отправляем сгенерированный документ всем пользователям
        sent_count = 0
        failed_count = 0
        
        for user in users:
            try:
                logger.info(f"Отправляю документ пользователю {user.telegram_id} ({user.first_name})")
                result = send_telegram_message(user.telegram_id, generated_content)
                
                if result and result.get('ok'):
                    sent_count += 1
                    logger.info(f"✅ Документ успешно отправлен пользователю {user.telegram_id}")
                else:
                    failed_count += 1
                    logger.error(f"Ошибка отправки документа пользователю {user.telegram_id}: {result}")
                    
                    # Если пользователь заблокировал бота, помечаем его как неактивного
                    if result and result.get('error_code') == 400:
                        description = result.get('description', '').lower()
                        if 'bot was blocked' in description or 'chat not found' in description:
                            user.is_active = False
                            user.save()
                            logger.info(f"Пользователь {user.telegram_id} помечен как неактивный")
                    
            except Exception as e:
                failed_count += 1
                logger.error(f"Исключение при отправке документа пользователю {user.telegram_id}: {str(e)}")
        
        logger.info(f"Документ сгенерирован и отправлен: {sent_count}/{total_users} пользователей")
        
        return JsonResponse({
            'ok': True,
            'generated_content': generated_content,
            'sent_count': sent_count,
            'failed_count': failed_count,
            'total_users': total_users
        })
        
    except json.JSONDecodeError as e:
        logger.error(f"Ошибка декодирования JSON: {e}")
        logger.error(f"Тело запроса: {request.body}")
        return JsonResponse({'error': 'Invalid JSON'}, status=400)
    except Exception as e:
        logger.error(f"Ошибка генерации документа: {e}")
        return JsonResponse({'error': str(e)}, status=500)

@csrf_exempt
def clear_cache_view(request):
    """Временный view для очистки кэша (удалить после использования)"""
    if request.method == 'POST':
        try:
            from django.core.cache import cache
            cache.clear()
            
            # Пересобираем статические файлы
            from django.core.management import call_command
            call_command('collectstatic', '--noinput', '--clear')
            
            return JsonResponse({
                'status': 'success',
                'message': 'Кэш очищен и статические файлы пересобраны'
            })
        except Exception as e:
            return JsonResponse({
                'status': 'error',
                'message': f'Ошибка: {str(e)}'
            }, status=500)
    
    return JsonResponse({
        'status': 'info',
        'message': 'Отправьте POST запрос для очистки кэша'
    })

@csrf_exempt
def export_document(request):
    """Экспорт сгенерированного документа в docx/pdf/xls (GET и POST)"""
    if request.method == 'POST':
        import json
        data = json.loads(request.body)
        doc_id = data.get('id')
        file_format = data.get('format', '').lower()
        content = None
        if doc_id:
            try:
                temp_doc = TemporaryDocument.objects.get(id=doc_id)
                content = temp_doc.content
            except TemporaryDocument.DoesNotExist:
                return JsonResponse({'error': 'Документ не найден'}, status=404)
        else:
            content = data.get('content', '').strip()
    elif request.method == 'GET':
        doc_id = request.GET.get('id')
        file_format = request.GET.get('format', '').lower()
        content = None
        if doc_id:
            try:
                temp_doc = TemporaryDocument.objects.get(id=doc_id)
                content = temp_doc.content
            except TemporaryDocument.DoesNotExist:
                return JsonResponse({'error': 'Документ не найден'}, status=404)
        else:
            content = request.GET.get('content', '').strip()
    else:
        return JsonResponse({'error': 'Method not allowed'}, status=405)
    if not content or file_format not in ['docx', 'pdf', 'xls']:
        return JsonResponse({'error': 'Передайте id и format (docx/pdf/xls)'}, status=400)
    filename = f"document.{file_format}"
    if file_format == 'docx':
        doc = Document()
        for line in content.split('\n'):
            doc.add_paragraph(line)
        buf = io.BytesIO()
        doc.save(buf)
        buf.seek(0)
        return FileResponse(buf, as_attachment=True, filename=filename)
    elif file_format == 'pdf':
        pdf = FPDF()
        pdf.add_page()
        font_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'static', 'fonts', 'DejaVuSans.ttf')
        pdf.add_font('DejaVu', '', font_path, uni=True)
        pdf.set_font('DejaVu', '', 10)
        content = content.replace('🔹', '-')

        lines = content.split('\n')
        table_started = False
        table_data = []
        for line in lines:
            # Поиск начала таблицы
            if line.strip().startswith('|') and line.strip().endswith('|'):
                table_started = True
                table_data.append([cell.strip() for cell in line.strip('|').split('|')])
            elif table_started and (line.strip().startswith('|') and line.strip().endswith('|')):
                table_data.append([cell.strip() for cell in line.strip('|').split('|')])
            elif table_started and not (line.strip().startswith('|') and line.strip().endswith('|')):
                # Таблица закончилась, выводим её
                if table_data:
                    # Определяем количество столбцов по первой строке
                    num_cols = len(table_data[0]) if table_data else 5
                    col_width = (pdf.w - pdf.l_margin - pdf.r_margin) / num_cols
                    for row in table_data:
                        for i, cell in enumerate(row):
                            if i < num_cols:  # Проверяем индекс
                                pdf.cell(col_width, 8, cell, border=1)
                        pdf.ln(8)
                table_started = False
                table_data = []
                if line.strip():
                    pdf.ln(4)
                    pdf.multi_cell(0, 8, line)
            else:
                if line.strip():
                    safe_multicell(pdf, 0, 8, line, max_len=80)
                else:
                    pdf.ln(4)
        # Если таблица была в самом конце
        if table_data:
            num_cols = len(table_data[0]) if table_data else 5
            col_width = (pdf.w - pdf.l_margin - pdf.r_margin) / num_cols
            for row in table_data:
                for i, cell in enumerate(row):
                    if i < num_cols:  # Проверяем индекс
                        pdf.cell(col_width, 8, cell, border=1)
                pdf.ln(8)

        pdf_output = BytesIO()
        pdf.output(pdf_output)
        pdf_output.seek(0)
        response = HttpResponse(pdf_output, content_type='application/pdf')
        response['Content-Disposition'] = f'attachment; filename="document.pdf"'
        return response
    elif file_format == 'xls':
        lines = [l for l in content.split('\n') if l.strip()]
        df = pd.DataFrame({'Документ': lines})
        buf = io.BytesIO()
        with pd.ExcelWriter(buf, engine='xlsxwriter') as writer:
            df.to_excel(writer, index=False)
        buf.seek(0)
        return FileResponse(buf, as_attachment=True, filename=filename)
    else:
        return JsonResponse({'error': 'Неподдерживаемый формат'}, status=400)

def safe_multicell(pdf, width, height, text, max_len=80):
    # Если ширина 0, используем ширину страницы минус отступы
    if width == 0:
        width = pdf.w - pdf.l_margin - pdf.r_margin
    
    # Проверяем, что ширина достаточна для одного символа
    if width < 10:
        width = 100
    
    try:
        words = text.split(' ')
        current_line = ''
        for word in words:
            # Если слово слишком длинное — разбиваем его
            while len(word) > max_len:
                part = word[:max_len]
                word = word[max_len:]
                if current_line:
                    pdf.multi_cell(width, height, current_line)
                    current_line = ''
                pdf.multi_cell(width, height, part)
            # Если добавление слова превышает лимит — печатаем текущую строку
            if len(current_line) + len(word) + 1 > max_len:
                if current_line:
                    pdf.multi_cell(width, height, current_line)
                current_line = word
            else:
                if current_line:
                    current_line += ' ' + word
                else:
                    current_line = word
        if current_line:
            pdf.multi_cell(width, height, current_line)
    except FPDFException as e:
        # Если возникла ошибка, просто добавляем текст как обычную строку
        pdf.ln(height)
        pdf.cell(0, height, text[:50] + '...' if len(text) > 50 else text)
