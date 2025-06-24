from django.db import models

class SpecodezhaSiz(models.Model):
    nazvanie = models.CharField(max_length=255, verbose_name="Название")
    edinica_izmereniya = models.CharField(max_length=50, verbose_name="Единица измерения")
    
    class Meta:
        verbose_name = "Спецодежда и СИЗ"
        verbose_name_plural = "Спецодежда и СИЗ"
    
    def __str__(self):
        return self.nazvanie