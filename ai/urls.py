from django.urls import path
from . import views

app_name = 'ai'

urlpatterns = [
    path('', views.index, name='index'),
    path('chat/', views.chat_interface, name='chat'),
    path('menu/', views.menu_generator, name='menu_generator'),
    path('api/chat/', views.chat_api, name='chat_api'),
    path('api/home-chat/', views.home_chat_api, name='home_chat_api'),
    path('api/generate-document/', views.generate_document, name='generate_document'),
    path('api/history/', views.chat_history, name='chat_history'),
    path('api/save-telegram-message/', views.save_telegram_message, name='save_telegram_message'),
] 