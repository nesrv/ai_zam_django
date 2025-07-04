from django.db import models
from django.utils import timezone


class Organizaciya(models.Model):
    nazvanie = models.CharField(max_length=300, verbose_name="Название")
    inn = models.CharField(max_length=12, unique=True, verbose_name="ИНН")
    
    class Meta:
        verbose_name = "Организация"
        verbose_name_plural = "Организации"
    
    def __str__(self):
        return f"{self.nazvanie} (ИНН: {self.inn})"


class Podrazdelenie(models.Model):
    kod = models.CharField(max_length=50, unique=True, verbose_name="Код")
    nazvanie = models.CharField(max_length=200, verbose_name="Название")
    
    class Meta:
        verbose_name = "Подразделение"
        verbose_name_plural = "Подразделения"
    
    def __str__(self):
        return f"{self.kod} - {self.nazvanie}"


class Specialnost(models.Model):
    nazvanie = models.CharField(max_length=200, verbose_name="Название специальности")
    
    class Meta:
        verbose_name = "Специальность"
        verbose_name_plural = "Специальности"
    
    def __str__(self):
        return self.nazvanie


class Sotrudnik(models.Model):
    organizaciya = models.ForeignKey(
        Organizaciya,
        on_delete=models.CASCADE,
        verbose_name="Организация",
        related_name="sotrudniki",
        null=True,
        blank=True
    )
    fio = models.CharField(max_length=300, verbose_name="ФИО")
    data_rozhdeniya = models.DateField(verbose_name="Дата рождения")
    specialnost = models.ForeignKey(
        Specialnost, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True,
        verbose_name="Специальность"
    )
    podrazdelenie = models.ForeignKey(
        Podrazdelenie,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name="Подразделение"
    )
    data_priema = models.DateField(verbose_name="Дата приема")
    data_nachala_raboty = models.DateField(verbose_name="Дата начала работы")
    
    class Meta:
        verbose_name = "Сотрудник"
        verbose_name_plural = "Сотрудники"
    
    def __str__(self):
        return self.fio


class DokumentySotrudnika(models.Model):
    sotrudnik = models.OneToOneField(
        Sotrudnik,
        on_delete=models.CASCADE,
        verbose_name="Сотрудник"
    )
    
    class Meta:
        verbose_name = "Документы сотрудника"
        verbose_name_plural = "Документы сотрудников"
    
    def __str__(self):
        return f"Документы - {self.sotrudnik.fio}"


class InstrukciiKartochki(models.Model):
    dokumenty_sotrudnika = models.ForeignKey(
        DokumentySotrudnika,
        on_delete=models.CASCADE,
        verbose_name="Документы сотрудника"
    )
    nazvanie = models.CharField(max_length=300, verbose_name="Название")
    tekst_kartochki = models.TextField(verbose_name="Текст карточки")
    soglasovan = models.BooleanField(default=False, verbose_name="Согласован")
    raspechatn = models.BooleanField(default=False, verbose_name="Распечатан")
    data_sozdaniya = models.DateTimeField(default=timezone.now, verbose_name="Дата создания")
    file_path = models.CharField(max_length=500, blank=True, null=True, verbose_name="Путь к файлу")
    
    class Meta:
        verbose_name = "Инструкция/карточка"
        verbose_name_plural = "Инструкции/карточки"
    
    def __str__(self):
        return self.nazvanie


class ProtokolyObucheniya(models.Model):
    dokumenty_sotrudnika = models.ForeignKey(
        DokumentySotrudnika,
        on_delete=models.CASCADE,
        verbose_name="Документы сотрудника"
    )
    nomer_programmy = models.CharField(max_length=50, verbose_name="Номер программы")
    nazvanie_kursa = models.CharField(max_length=200, verbose_name="Название курса")
    tekst_protokola = models.TextField(verbose_name="Текст протокола")
    data_prikaza = models.DateField(verbose_name="Дата приказа")
    data_dopuska = models.DateField(null=True, blank=True, verbose_name="Дата допуска")
    data_ocherednoy_proverki = models.DateField(null=True, blank=True, verbose_name="Дата очередной проверки")
    registracionnyy_nomer = models.CharField(max_length=50, verbose_name="Регистрационный номер")
    raspechatn = models.BooleanField(default=False, verbose_name="Распечатан")
    
    class Meta:
        verbose_name = "Протокол обучения"
        verbose_name_plural = "Протоколы обучения"
    
    def __str__(self):
        return f"{self.nomer_programmy} - {self.nazvanie_kursa}"


class Instruktazhi(models.Model):
    dokumenty_sotrudnika = models.ForeignKey(
        DokumentySotrudnika,
        on_delete=models.CASCADE,
        verbose_name="Документы сотрудника"
    )
    data_instruktazha = models.DateField(verbose_name="Дата инструктажа")
    vid_instruktazha = models.CharField(max_length=100, verbose_name="Вид инструктажа")
    tekst_instruktazha = models.TextField(verbose_name="Текст инструктажа")
    instruktor = models.CharField(max_length=150, verbose_name="Инструктор")
    data_ocherednogo_instruktazha = models.DateField(verbose_name="Дата очередного инструктажа")
    raspechatn = models.BooleanField(default=False, verbose_name="Распечатан")
    
    class Meta:
        verbose_name = "Инструктаж"
        verbose_name_plural = "Инструктажи"
    
    def __str__(self):
        return f"{self.vid_instruktazha} - {self.data_instruktazha}"


class VidyDokumentov(models.Model):
    TIP_CHOICES = [
        ('dokument', 'Документ'),
        ('protokol', 'Протокол'),
        ('instruktazh', 'Инструктаж'),
    ]
    
    nazvanie = models.CharField(max_length=200, verbose_name="Название")
    tip = models.CharField(max_length=20, choices=TIP_CHOICES, verbose_name="Тип")
    
    class Meta:
        verbose_name = "Вид документа"
        verbose_name_plural = "Виды документов"
    
    def __str__(self):
        return f"{self.nazvanie} ({self.get_tip_display()})"

