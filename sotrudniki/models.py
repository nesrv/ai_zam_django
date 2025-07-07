from django.db import models
from django.utils import timezone
from django.core.validators import FileExtensionValidator


class Organizaciya(models.Model):
    nazvanie = models.CharField(max_length=300, verbose_name="Название")
    inn = models.CharField(max_length=12, unique=True, verbose_name="ИНН")
    ogrn = models.CharField(max_length=15, verbose_name="ОГРН", null=True, blank=True)
    adres = models.TextField(verbose_name="Адрес", null=True, blank=True)
    is_active = models.BooleanField(default=True, verbose_name="Активная")
    
    class Meta:
        verbose_name = "Организация"
        verbose_name_plural = "Организации"
    
    def __str__(self):
        return f"{self.nazvanie} (ИНН: {self.inn})"


class Podrazdelenie(models.Model):
    organizaciya = models.ForeignKey(
        'Organizaciya',
        on_delete=models.CASCADE,
        verbose_name="Организация",
        related_name="podrazdeleniya",
        null=True,
        blank=True
    )
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
    POL_CHOICES = [
        ('мужской', 'Мужской'),
        ('женский', 'Женский'),
    ]
    
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
    pol = models.CharField(
        max_length=10,
        choices=POL_CHOICES,
        verbose_name="Пол",
        null=True,
        blank=True
    )
    razmer_odezhdy = models.CharField(
        max_length=10,
        default="50-52",
        verbose_name="Размер одежды"
    )
    razmer_obuvi = models.CharField(
        max_length=5,
        default="43",
        verbose_name="Размер обуви"
    )
    razmer_golovnogo_ubora = models.CharField(
        max_length=5,
        default="55",
        verbose_name="Размер головного убора"
    )
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
    shablon_instrukcii = models.URLField(max_length=500, null=True, blank=True, verbose_name="Шаблон инструкции")
    soglasovan = models.BooleanField(default=False, verbose_name="Согласован")
    raspechatn = models.BooleanField(default=False, verbose_name="Распечатан")
    data_sozdaniya = models.DateTimeField(default=timezone.now, verbose_name="Дата создания")
    
    class Meta:
        verbose_name = "Инструкция/карточка"
        verbose_name_plural = "Инструкции/карточки"
    
    def __str__(self):
        return self.nazvanie


class SotrudnikiShablonyProtokolov(models.Model):
    nomer_programmy = models.CharField(max_length=50, verbose_name="№ программы")
    kurs = models.CharField(max_length=200, verbose_name="Курс")
    html_file = models.FileField(
        upload_to='instruction_templates/',
        validators=[FileExtensionValidator(allowed_extensions=['html'])],
        verbose_name="HTML файл протокола",
        help_text="Загрузите HTML файл с шаблоном протокола"
    )
    
    class Meta:
        verbose_name = "Сотрудники шаблоны протоколов"
        verbose_name_plural = "Сотрудники шаблоны протоколов"
    
    def __str__(self):
        return f"{self.nomer_programmy} - {self.kurs}"



class ProtokolyObucheniya(models.Model):
    sotrudnik = models.ForeignKey(
        Sotrudnik,
        on_delete=models.CASCADE,
        verbose_name="Сотрудник",
        related_name="protokoly_obucheniya"
    )
    shablon_protokola = models.ForeignKey(
        SotrudnikiShablonyProtokolov,
        on_delete=models.CASCADE,
        verbose_name="Шаблон протокола"
    )
    data_prikaza = models.DateField(verbose_name="Дата приказа")
    data_protokola_dopuska = models.DateField(verbose_name="Дата протокола/приказа-допуска")
    data_dopuska_k_rabote = models.DateField(verbose_name="Дата допуска к работе")
    data_ocherednoy_proverki = models.DateField(null=True, blank=True, verbose_name="Дата очередной проверки")
    registracionnyy_nomer = models.CharField(max_length=50, verbose_name="Рег №")
    raspechatn = models.BooleanField(default=False, verbose_name="Распеч")
    
    class Meta:
        verbose_name = "Протокол обучения"
        verbose_name_plural = "Протоколы обучения"
    
    def __str__(self):
        return f"{self.shablon_protokola} - {self.registracionnyy_nomer}"


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


class ShablonyDokumentovPoSpecialnosti(models.Model):
    specialnost = models.OneToOneField(
        Specialnost,
        on_delete=models.CASCADE,
        verbose_name="Специальность",
        related_name="shablony_dokumentov"
    )
    dolzhnostnaya_instrukciya = models.FileField(
        upload_to='document_templates/',
        validators=[FileExtensionValidator(allowed_extensions=['html'])],
        verbose_name="HTML файл должностной инструкции",
        help_text="Загрузите HTML файл с шаблоном должностной инструкции",
        null=True,
        blank=True
    )
    lichnaya_kartochka_rabotnika = models.FileField(
        upload_to='document_templates/',
        validators=[FileExtensionValidator(allowed_extensions=['html'])],
        verbose_name="HTML файл личной карточки работника",
        help_text="Загрузите HTML файл с шаблоном личной карточки работника",
        null=True,
        blank=True
    )
    lichnaya_kartochka_siz = models.FileField(
        upload_to='document_templates/',
        validators=[FileExtensionValidator(allowed_extensions=['html'])],
        verbose_name="HTML файл личной карточки учета выдачи СИЗ",
        help_text="Загрузите HTML файл с шаблоном личной карточки учета выдачи СИЗ",
        null=True,
        blank=True
    )
    karta_ocenki_riskov = models.FileField(
        upload_to='document_templates/',
        validators=[FileExtensionValidator(allowed_extensions=['html'])],
        verbose_name="HTML файл карты оценки проф. рисков",
        help_text="Загрузите HTML файл с шаблоном карты оценки проф. рисков",
        null=True,
        blank=True
    )
    instrukciya_po_ohrane_truda = models.FileField(
        upload_to='document_templates/',
        validators=[FileExtensionValidator(allowed_extensions=['html'])],
        verbose_name="HTML файл инструкции по охране труда",
        help_text="Загрузите HTML файл с шаблоном инструкции по охране труда",
        null=True,
        blank=True,
        default="document_templates/instrukciya_po_ohrane_truda_template.html"
    )
    
    class Meta:
        verbose_name = "Шаблоны документов по специальности"
        verbose_name_plural = "Шаблоны документов по специальностям"
    
    def __str__(self):
        return f"Шаблоны для {self.specialnost.nazvanie}"

