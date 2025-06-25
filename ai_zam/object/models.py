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

# Специальности и кадры
class Specialnost(models.Model):
    nazvanie = models.CharField(max_length=255, verbose_name="Название специальности")
    
    class Meta:
        verbose_name = "Специальность"
        verbose_name_plural = "Специальности"
    
    def __str__(self):
        return self.nazvanie

class Kadry(models.Model):
    fio = models.CharField(max_length=255, verbose_name="ФИО")
    specialnost = models.ForeignKey(Specialnost, on_delete=models.CASCADE, verbose_name="Специальность", related_name="kadry")
    razryad = models.CharField(max_length=50, verbose_name="Разряд")
    pasport = models.CharField(max_length=100, verbose_name="Паспорт")
    telefon = models.CharField(max_length=20, verbose_name="Телефон")
    
    class Meta:
        verbose_name = "Кадр"
        verbose_name_plural = "Кадры"
        db_table = 'kadry'
    
    def __str__(self):
        return self.fio

# Объект
class Objekt(models.Model):
    STATUS_CHOICES = [
        ('планируется', 'Планируется'),
        ('в работе', 'В работе'),
        ('завершён', 'Завершён'),
    ]
    
    nazvanie = models.CharField(max_length=255, verbose_name="Название")
    otvetstvennyj = models.ForeignKey(Kadry, on_delete=models.SET_NULL, null=True, blank=True, verbose_name="Ответственный")
    data_nachala = models.DateField(verbose_name="Дата начала")
    data_plan_zaversheniya = models.DateField(verbose_name="Дата план завершения")
    data_fakt_zaversheniya = models.DateField(null=True, blank=True, verbose_name="Дата факт завершения")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='планируется', verbose_name="Статус")
    
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
    
    def __str__(self):
        return f"{self.fakticheskij_resurs} - {self.data} ({self.izraskhodovano})"
