from django.urls import path
from . import views

app_name = 'telegrambot'

urlpatterns = [
    path('', views.bot_status, name='status'),  # Главная страница - статус
    path('dashboard/', views.bot_dashboard, name='dashboard'),  # Dashboard на отдельной странице
    path('webhook/', views.telegram_webhook, name='webhook'),
    path('webhook/status/', views.webhook_status, name='webhook_status'),
    path('management/', views.bot_management, name='management'),
    path('broadcast/', views.send_broadcast, name='broadcast'),
] 