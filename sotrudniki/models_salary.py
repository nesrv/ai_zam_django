from django.db import models
from .models import Sotrudnik
from object.models import Objekt

class SotrudnikiZarplaty(models.Model):
    sotrudnik = models.ForeignKey(Sotrudnik, on_delete=models.CASCADE, verbose_name="Сотрудник")
    objekt = models.ForeignKey(Objekt, on_delete=models.CASCADE, verbose_name="Объект")
    data = models.DateField(verbose_name="Дата")
    kolichestvo_chasov = models.DecimalField(max_digits=8, decimal_places=2, verbose_name="Количество часов")
    kpi = models.DecimalField(max_digits=5, decimal_places=2, default=1.0, verbose_name="KPI")
    
    class Meta:
        verbose_name = "Зарплата сотрудника"
        verbose_name_plural = "Зарплаты сотрудников"
        db_table = 'sotrudniki_zarplaty'
        unique_together = ['sotrudnik', 'objekt', 'data']
    
    def __str__(self):
        return f"{self.sotrudnik.fio} - {self.objekt.nazvanie} ({self.data})"