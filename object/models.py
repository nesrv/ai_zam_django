from django.db import models

# Категория ресурса
class KategoriyaResursa(models.Model):
    nazvanie = models.CharField(max_length=255, verbose_name="Название")
    
    class Meta:
        verbose_name = "Категория ресурса"
        verbose_name_plural = "Категории ресурсов"
        db_table = 'kategoriya_resursa'
    
    def __str__(self):
        return self.nazvanie

# Ресурс
class Resurs(models.Model):
    naimenovanie = models.CharField(max_length=255, verbose_name="Наименование")
    edinica_izmereniya = models.CharField(max_length=50, verbose_name="Единица измерения")
    kategoriya_resursa = models.ForeignKey(KategoriyaResursa, on_delete=models.CASCADE, verbose_name="Категория ресурса")
    
    class Meta:
        verbose_name = "Ресурс"
        verbose_name_plural = "Ресурсы"
        db_table = 'resurs'
    
    def __str__(self):
        return self.naimenovanie



# Объект
class Objekt(models.Model):
    STATUS_CHOICES = [
        ('планируется', 'Планируется'),
        ('в работе', 'В работе'),
        ('завершён', 'Завершён'),
    ]
    
    nazvanie = models.CharField(max_length=255, verbose_name="Название")
    organizaciya = models.ForeignKey(
        'sotrudniki.Organizaciya',
        on_delete=models.CASCADE,
        verbose_name="Организация",
        related_name="objekty",
        null=True,
        blank=True
    )
    otvetstvennyj = models.CharField(max_length=255, default="Иванов Иван Иванович", verbose_name="Ответственный")
    data_nachala = models.DateField(verbose_name="Дата начала")
    data_plan_zaversheniya = models.DateField(verbose_name="Дата план завершения")
    data_fakt_zaversheniya = models.DateField(null=True, blank=True, verbose_name="Дата факт завершения")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='планируется', verbose_name="Статус")
    is_active = models.BooleanField(default=True, verbose_name="Активный")
    
    class Meta:
        verbose_name = "Объект"
        verbose_name_plural = "Объекты"
        db_table = 'objekt'
    
    def __str__(self):
        return self.nazvanie

# Ресурсы по объекту
class ResursyPoObjektu(models.Model):
    objekt = models.ForeignKey(Objekt, on_delete=models.CASCADE, verbose_name="Объект")
    resurs = models.ForeignKey(Resurs, on_delete=models.CASCADE, verbose_name="Ресурс")
    kolichestvo = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Количество")
    cena = models.DecimalField(max_digits=12, decimal_places=2, verbose_name="Цена")
    potracheno = models.DecimalField(max_digits=10, decimal_places=2, default=0, verbose_name="Потрачено лимитов")
    
    class Meta:
        verbose_name = "Ресурсы по объекту"
        verbose_name_plural = "Ресурсы по объектам"
        db_table = 'resursy_po_objektu'
    
    def __str__(self):
        return f"{self.objekt.nazvanie} - {self.resurs.naimenovanie}"

class FakticheskijResursPoObjektu(models.Model):
    resurs_po_objektu = models.OneToOneField(ResursyPoObjektu, on_delete=models.CASCADE, verbose_name="Ресурс по объекту")
    
    class Meta:
        verbose_name = "Фактический ресурс по объекту"
        verbose_name_plural = "Фактические ресурсы по объектам"
        db_table = 'fakticheskij_resurs_po_objektu'
    
    def __str__(self):
        return f"Факт: {self.resurs_po_objektu}"

class RaskhodResursa(models.Model):
    fakticheskij_resurs = models.ForeignKey(FakticheskijResursPoObjektu, on_delete=models.CASCADE, verbose_name="Фактический ресурс")
    data = models.DateField(verbose_name="Дата")
    izraskhodovano = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Израсходовано")
    
    class Meta:
        verbose_name = "Расход ресурса"
        verbose_name_plural = "Расходы ресурсов"
        db_table = 'raskhod_resursa'
        unique_together = ['fakticheskij_resurs', 'data']
    
    def __str__(self):
        return f"{self.fakticheskij_resurs} - {self.data} ({self.izraskhodovano})"

class DokhodResursa(models.Model):
    fakticheskij_resurs = models.ForeignKey(FakticheskijResursPoObjektu, on_delete=models.CASCADE, verbose_name="Фактический ресурс")
    data = models.DateField(verbose_name="Дата")
    vypolneno = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Выполнено")

    class Meta:
        verbose_name = "Доход ресурса"
        verbose_name_plural = "Доходы ресурсов"
        db_table = 'dokhod_resursa'
        unique_together = ['fakticheskij_resurs', 'data']

    def __str__(self):
        return f"{self.fakticheskij_resurs} - {self.data} (Выполнено: {self.vypolneno})"

class SvodnayaRaskhodDokhodPoDnyam(models.Model):
    objekt = models.ForeignKey(Objekt, on_delete=models.CASCADE, verbose_name="Объект")
    data = models.DateField(verbose_name="Дата")
    raskhod = models.DecimalField(max_digits=12, decimal_places=2, default=0, verbose_name="Расход")
    dokhod = models.DecimalField(max_digits=12, decimal_places=2, default=0, verbose_name="Доход")
    balans = models.DecimalField(max_digits=12, decimal_places=2, default=0, verbose_name="Баланс")
    
    class Meta:
        verbose_name = "Сводная по дням"
        verbose_name_plural = "Сводная по дням"
        db_table = 'svodnaya_raskhod_dokhod_po_dnyam'
        unique_together = ['objekt', 'data']
    
    def __str__(self):
        return f"{self.objekt.nazvanie} - {self.data} (Баланс: {self.balans})"

class KategoriyaPoObjektu(models.Model):
    objekt = models.ForeignKey(Objekt, on_delete=models.CASCADE, verbose_name="Объект")
    kategoriya = models.ForeignKey(KategoriyaResursa, on_delete=models.CASCADE, verbose_name="Категория")
    
    class Meta:
        verbose_name = "Категория по объекту"
        verbose_name_plural = "Категории по объектам"
        db_table = 'kategoriya_po_objektu'
        unique_together = ['objekt', 'kategoriya']
    
    def __str__(self):
        return f"{self.objekt.nazvanie} - {self.kategoriya.nazvanie}"
