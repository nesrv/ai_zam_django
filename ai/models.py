from django.db import models
from django.contrib.auth.models import User
import json

# Create your models here.

class AIModel(models.Model):
    name = models.CharField(max_length=100, verbose_name="Название модели")
    description = models.TextField(verbose_name="Описание")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Дата создания")
    is_active = models.BooleanField(default=True, verbose_name="Активна")
    
    class Meta:
        verbose_name = "AI Модель"
        verbose_name_plural = "AI Модели"
    
    def __str__(self):
        return self.name

class ChatSession(models.Model):
    session_id = models.CharField(max_length=50, unique=True, verbose_name="ID сессии")
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True, verbose_name="Пользователь")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Дата создания")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Дата обновления")
    is_active = models.BooleanField(default=True, verbose_name="Активна")
    
    class Meta:
        verbose_name = "Сессия чата"
        verbose_name_plural = "Сессии чата"
    
    def __str__(self):
        return f"Сессия {self.session_id}"

class ChatMessage(models.Model):
    MESSAGE_TYPES = [
        ('user', 'Пользователь'),
        ('assistant', 'Ассистент'),
        ('system', 'Система'),
    ]
    
    session = models.ForeignKey(ChatSession, on_delete=models.CASCADE, related_name='messages', verbose_name="Сессия")
    message_type = models.CharField(max_length=10, choices=MESSAGE_TYPES, verbose_name="Тип сообщения")
    content = models.TextField(verbose_name="Содержание")
    file = models.FileField(upload_to='documents_ai/', null=True, blank=True, verbose_name="Файл")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Дата создания")
    
    class Meta:
        verbose_name = "Сообщение чата"
        verbose_name_plural = "Сообщения чата"
        ordering = ['created_at']
    
    def __str__(self):
        return f"{self.get_message_type_display()}: {self.content[:50]}..."

class AIPrompt(models.Model):
    nazvanie = models.CharField(max_length=200, verbose_name="Название")
    zapros = models.TextField(verbose_name="Запрос")
    struktura_otveta = models.JSONField(verbose_name="Структура ответа", help_text="JSON структура ожидаемого ответа")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Дата создания")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Дата обновления")
    is_active = models.BooleanField(default=True, verbose_name="Активен")
    
    class Meta:
        verbose_name = "AI Промпт"
        verbose_name_plural = "AI Промпты"
        ordering = ['nazvanie']
    
    def __str__(self):
        return self.nazvanie
