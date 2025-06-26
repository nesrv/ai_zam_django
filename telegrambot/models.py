from django.db import models
from django.contrib.auth.models import User

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
