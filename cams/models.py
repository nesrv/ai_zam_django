from django.db import models

class Camera(models.Model):
    # Основные данные
    name = models.CharField(max_length=100, verbose_name="Название камеры")
    url = models.CharField(max_length=255, verbose_name="url")
    objekt = models.ForeignKey('object.Objekt', on_delete=models.SET_NULL, verbose_name="Объект", related_name="cameras", null=True, blank=True)
   
    # Местоположение
    location = models.CharField(max_length=200, blank=True, verbose_name="Местоположение")
    description = models.TextField(blank=True, verbose_name="Описание")

    # Статус и настройки
    is_active = models.BooleanField(default=True, verbose_name="Активна")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Дата добавления")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Последнее обновление")

    def __str__(self):
        return f"{self.name} ({self.url})"

    class Meta:
        verbose_name = "Камера"
        verbose_name_plural = "Камеры"
