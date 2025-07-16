from django.urls import path
from . import views
from .views_chatbots import chatbots_page, update_chat_id

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
] 