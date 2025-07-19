from django.urls import path
from . import views
from .views_chatbots import chatbots_page, update_chat_id, get_chat_messages_ajax as get_chatbot_messages_ajax, send_message_to_chat as send_chatbot_message
from .views_chat_messages import chat_messages_list, chat_messages_detail, send_message_to_chat, get_chat_messages_ajax
from .views_stats import messages_stats
from .views_employees import get_employees_by_object

app_name = 'telegrambot'

urlpatterns = [
    
    path('', chatbots_page, name='chatbots_page'),  # Главная страница - чат-боты
    path('status/', views.bot_status, name='status'),  # Статус бота
    path('dashboard/', views.bot_dashboard, name='dashboard'),  # Dashboard на отдельной странице
    path('webhook/', views.telegram_webhook, name='webhook'),
    path('webhook/status/', views.webhook_status, name='webhook_status'),
    path('management/', views.bot_management, name='management'),
    path('broadcast/', views.send_broadcast, name='broadcast'),
    path('generate-document/', views.generate_document, name='generate_document'),
    path('clear-cache/', views.clear_cache_view, name='clear_cache'),  # Временный URL для очистки кэша
    path('export-document/', views.export_document, name='export_document'),
    path('create-object-ai/', views.create_object_ai, name='create_object_ai'),
    path('create-object-from-message/', views.create_object_from_message, name='create_object_from_message'),
    path('create-object-from-json/', views.create_object_from_json, name='create_object_from_json'),
    path('send-file-to-deepseek/', views.send_file_to_deepseek, name='send_file_to_deepseek'),
    path('download-and-save/', views.download_and_save_document, name='download_and_save_document'),
    path('save-json-response/', views.save_json_response, name='save_json_response'),
    path('update-chat-id/', update_chat_id, name='update_chat_id'),
    
    # Старые URL для совместимости
    path('get-chat-messages/', get_chatbot_messages_ajax, name='get_chatbot_messages'),
    path('send-message/', send_chatbot_message, name='send_chatbot_message'),
    
    # Новые URL для работы с сообщениями из чатов
    path('chats/', chat_messages_list, name='chat_messages_list'),
    path('chats/<str:chat_id>/', chat_messages_detail, name='chat_messages_detail'),
    path('chats/<str:chat_id>/send/', send_message_to_chat, name='send_message_to_chat'),
    path('chats/<str:chat_id>/messages/', get_chat_messages_ajax, name='get_chat_messages_ajax'),
    
    # Статистика сообщений
    path('stats/', messages_stats, name='messages_stats'),
    
    # API для получения сотрудников по объекту
    path('get-employees-by-object/', get_employees_by_object, name='get_employees_by_object'),
    
    # API для поиска сотрудников по фамилии и объекту
    path('find-employees/', views.find_employees, name='find_employees'),
] 