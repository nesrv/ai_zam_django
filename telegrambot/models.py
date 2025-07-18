from django.db import models
from django.contrib.auth.models import User
from uuid import uuid4

class TelegramUser(models.Model):
    """Модель для хранения информации о пользователях Telegram"""
    telegram_id = models.BigIntegerField(unique=True, verbose_name="Telegram ID")
    username = models.CharField(max_length=100, blank=True, null=True, verbose_name="Username")
    first_name = models.CharField(max_length=100, blank=True, null=True, verbose_name="Имя")
    last_name = models.CharField(max_length=100, blank=True, null=True, verbose_name="Фамилия")
    is_active = models.BooleanField(default=True, verbose_name="Активен")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Дата регистрации")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Дата обновления")
    
    class Meta:
        verbose_name = "Пользователь Telegram"
        verbose_name_plural = "Пользователи Telegram"
    
    def __str__(self):
        return f"{self.first_name} (@{self.username}) - {self.telegram_id}"

class TelegramMessage(models.Model):
    """Модель для хранения сообщений Telegram"""
    MESSAGE_TYPES = [
        ('text', 'Текст'),
        ('command', 'Команда'),
        ('button', 'Кнопка'),
    ]
    
    user = models.ForeignKey(TelegramUser, on_delete=models.CASCADE, related_name='messages', verbose_name="Пользователь")
    message_type = models.CharField(max_length=10, choices=MESSAGE_TYPES, default='text', verbose_name="Тип сообщения")
    content = models.TextField(verbose_name="Содержание")
    is_from_user = models.BooleanField(default=True, verbose_name="От пользователя")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Дата создания")
    
    class Meta:
        verbose_name = "Сообщение Telegram"
        verbose_name_plural = "Сообщения Telegram"
        ordering = ['created_at']
    
    def __str__(self):
        direction = "→" if self.is_from_user else "←"
        return f"{direction} {self.user.first_name}: {self.content[:50]}..."

class TemporaryDocument(models.Model):
    """Временное хранилище сгенерированных документов для скачивания"""
    id = models.UUIDField(primary_key=True, default=uuid4, editable=False)
    user = models.ForeignKey(TelegramUser, on_delete=models.CASCADE, related_name='temp_documents', verbose_name="Пользователь")
    content = models.TextField(verbose_name="Содержание документа")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Дата создания")

    class Meta:
        verbose_name = "Временный документ"
        verbose_name_plural = "Временные документы"
        ordering = ['-created_at']

    def __str__(self):
        return f"Документ {self.id} для {self.user}";

class ChatMessage(models.Model):
    chat_id = models.CharField(max_length=255, verbose_name="ID чата")
    message_text = models.TextField(verbose_name="Текст сообщения")
    from_user = models.CharField(max_length=255, verbose_name="От пользователя")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Дата создания")
    message_id = models.BigIntegerField(null=True, blank=True, verbose_name="ID сообщения")
    reply_to_message_id = models.BigIntegerField(null=True, blank=True, verbose_name="ID сообщения, на которое отвечают")
    forward_from = models.JSONField(null=True, blank=True, verbose_name="Информация о пересланном сообщении")
    
    class Meta:
        verbose_name = "Сообщение чата"
        verbose_name_plural = "Сообщения чатов"
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['chat_id']),
            models.Index(fields=['message_id']),
        ]
    
    def __str__(self):
        return f"{self.from_user}: {self.message_text[:50]}"
        
    def is_reply(self):
        """Проверяет, является ли сообщение ответом на другое"""
        return self.reply_to_message_id is not None
        
    def is_forwarded(self):
        """Проверяет, является ли сообщение пересланным"""
        return self.forward_from is not None


class ProcessedUpdate(models.Model):
    """Модель для отслеживания обработанных обновлений Telegram"""
    update_id = models.CharField(max_length=50, unique=True, verbose_name="ID обновления")
    processed_at = models.DateTimeField(auto_now_add=True, verbose_name="Дата обработки")
    
    class Meta:
        verbose_name = "Обработанное обновление"
        verbose_name_plural = "Обработанные обновления"
        ordering = ['-processed_at']
        indexes = [
            models.Index(fields=['update_id']),
            models.Index(fields=['processed_at']),
        ]
    
    def __str__(self):
        return f"Обновление {self.update_id} обработано {self.processed_at}"
