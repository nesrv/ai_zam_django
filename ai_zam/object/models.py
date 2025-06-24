from django.db import models

# Ресурсы
class SpecodezhaSiz(models.Model):
    nazvanie = models.CharField(max_length=255, verbose_name="Название")
    edinica_izmereniya = models.CharField(max_length=50, verbose_name="Единица измерения")
    
    class Meta:
        verbose_name = "Спецодежда и СИЗ"
        verbose_name_plural = "Спецодежда и СИЗ"
    
    def __str__(self):
        return self.nazvanie

class AdministrativnoBytovyeRashody(models.Model):
    nazvanie = models.CharField(max_length=255, verbose_name="Название")
    edinica_izmereniya = models.CharField(max_length=50, verbose_name="Единица измерения")
    
    class Meta:
        verbose_name = "Административно-бытовые расходы"
        verbose_name_plural = "Административно-бытовые расходы"
    
    def __str__(self):
        return self.nazvanie

class InstrumentMaterialy(models.Model):
    nazvanie = models.CharField(max_length=255, verbose_name="Название")
    edinica_izmereniya = models.CharField(max_length=50, verbose_name="Единица измерения")
    
    class Meta:
        verbose_name = "Инструмент и материалы"
        verbose_name_plural = "Инструмент и материалы"
    
    def __str__(self):
        return self.nazvanie

class MashinyMekhanizmy(models.Model):
    nazvanie = models.CharField(max_length=255, verbose_name="Название")
    edinica_izmereniya = models.CharField(max_length=50, verbose_name="Единица измерения")
    
    class Meta:
        verbose_name = "Машины и механизмы"
        verbose_name_plural = "Машины и механизмы"
    
    def __str__(self):
        return self.nazvanie

class KadrovoeObespechenie(models.Model):
    naimenovanie = models.CharField(max_length=255, verbose_name="Наименование")
    edinica_izmereniya = models.CharField(max_length=50, verbose_name="Единица измерения")
    
    class Meta:
        verbose_name = "Кадровое обеспечение"
        verbose_name_plural = "Кадровое обеспечение"
    
    def __str__(self):
        return self.naimenovanie

class PodryadnyeOrganizacii(models.Model):
    naimenovanie = models.CharField(max_length=255, verbose_name="Наименование")
    edinica_izmereniya = models.CharField(max_length=50, verbose_name="Единица измерения")
    
    class Meta:
        verbose_name = "Подрядные организации"
        verbose_name_plural = "Подрядные организации"
    
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
    
    def __str__(self):
        return self.fio
