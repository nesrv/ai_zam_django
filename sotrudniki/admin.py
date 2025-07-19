from django.contrib import admin
from .models import (
    Organizaciya, Podrazdelenie, Specialnost, Sotrudnik, SotrudnikiZarplaty,
    ProtokolyObucheniya, ShablonyDokumentovPoSpecialnosti, SotrudnikiShablonyProtokolov, Instruktazhi, DokumentySotrudnika, ShablonyInstruktazhej
)
from object.models import Objekt


@admin.register(Organizaciya)
class OrganizaciyaAdmin(admin.ModelAdmin):
    list_display = ['nazvanie', 'inn', 'ogrn', 'is_active']
    search_fields = ['nazvanie', 'inn', 'ogrn']
    fields = ['nazvanie', 'inn', 'ogrn', 'adres', 'is_active']


@admin.register(Podrazdelenie)
class PodrazdelenieAdmin(admin.ModelAdmin):
    list_display = ['kod', 'nazvanie']
    search_fields = ['kod', 'nazvanie']


class ShablonyDokumentovPoSpecialnostiInline(admin.StackedInline):
    model = ShablonyDokumentovPoSpecialnosti
    extra = 0
    fields = ['dolzhnostnaya_instrukciya', 'lichnaya_kartochka_rabotnika', 'lichnaya_kartochka_siz', 'karta_ocenki_riskov', 'instrukciya_po_ohrane_truda']


@admin.register(Specialnost)
class SpecialnostAdmin(admin.ModelAdmin):
    list_display = ['nazvanie', 'get_sotrudniki_count']
    search_fields = ['nazvanie']
    inlines = [ShablonyDokumentovPoSpecialnostiInline]
    
    def get_sotrudniki_count(self, obj):
        return obj.sotrudnik_set.count()
    get_sotrudniki_count.short_description = 'Количество сотрудников'


class ProtokolyObucheniyaInline(admin.TabularInline):
    model = ProtokolyObucheniya
    extra = 0


class InstruktazhiInline(admin.TabularInline):
    model = Instruktazhi
    fk_name = 'sotrudnik'
    extra = 0
    fields = ['instruktazh', 'data_provedeniya', 'instruktor']


class ObjektyInline(admin.TabularInline):
    model = Objekt.sotrudniki.through
    verbose_name = "Объекты"
    verbose_name_plural = "Объекты"
    extra = 0
    fk_name = 'sotrudnik'
    fields = ['objekt']
    can_delete = True


@admin.register(Sotrudnik)
class SotrudnikAdmin(admin.ModelAdmin):
    list_display = ['fio', 'organizaciya', 'specialnost', 'podrazdelenie', 'data_priema', 'data_nachala_raboty', 
                   'bazovoe_obuchenie', 'obuchenie_na_predpriyatii', 'med_osvidetelstvovanie', 'dopusk_k_rabote', 'stazhirovka', 'siz', 'get_objekty']
    list_filter = ['organizaciya', 'specialnost', 'podrazdelenie', 'data_priema', 
                  'bazovoe_obuchenie', 'obuchenie_na_predpriyatii', 'med_osvidetelstvovanie', 'dopusk_k_rabote', 'stazhirovka', 'siz']
    search_fields = ['fio']
    date_hierarchy = 'data_priema'
    inlines = [ProtokolyObucheniyaInline, InstruktazhiInline, ObjektyInline]
    readonly_fields = ['get_shablony_dokumentov']
    # Связь с объектами реализована через поле sotrudniki в модели Objekt
    fieldsets = [
        ('Основная информация', {
            'fields': ['fio', 'organizaciya', 'specialnost', 'podrazdelenie', 'data_rozhdeniya', 'pol']
        }),
        ('Даты', {
            'fields': ['data_priema', 'data_nachala_raboty']
        }),
        ('Размеры', {
            'fields': ['razmer_odezhdy', 'razmer_obuvi', 'razmer_golovnogo_ubora']
        }),
        ('Статусы', {
            'fields': ['bazovoe_obuchenie', 'obuchenie_na_predpriyatii', 'med_osvidetelstvovanie', 'dopusk_k_rabote', 'stazhirovka', 'siz']
        }),
        ('Объекты', {
            'fields': [],
            'description': 'Объекты назначаются через раздел Объекты'
        }),
        ('Документы', {
            'fields': ['get_shablony_dokumentov']
        }),
    ]
    
    def get_shablony_dokumentov(self, obj):
        if obj.specialnost and hasattr(obj.specialnost, 'shablony_dokumentov'):
            shablony = obj.specialnost.shablony_dokumentov
            docs = []
            if shablony.dolzhnostnaya_instrukciya:
                docs.append(f"Должностная инструкция: {shablony.dolzhnostnaya_instrukciya.name}")
            if shablony.lichnaya_kartochka_rabotnika:
                docs.append(f"Личная карточка работника: {shablony.lichnaya_kartochka_rabotnika.name}")
            if shablony.lichnaya_kartochka_siz:
                docs.append(f"Личная карточка СИЗ: {shablony.lichnaya_kartochka_siz.name}")
            if shablony.karta_ocenki_riskov:
                docs.append(f"Карта оценки рисков: {shablony.karta_ocenki_riskov.name}")
            if shablony.instrukciya_po_ohrane_truda:
                docs.append(f"Инструкция по охране труда: {shablony.instrukciya_po_ohrane_truda.name}")
            return "\n".join(docs) if docs else "Нет документов"
        return "Специальность не указана или нет шаблонов"
    get_shablony_dokumentov.short_description = "Документы по специальности"
    
    def get_objekty(self, obj):
        return ", ".join([objekt.nazvanie for objekt in obj.objekty_work.all()])
    get_objekty.short_description = "Объекты"






@admin.register(ShablonyDokumentovPoSpecialnosti)
class ShablonyDokumentovPoSpecialnostiAdmin(admin.ModelAdmin):
    list_display = ['specialnost', 'dolzhnostnaya_instrukciya', 'lichnaya_kartochka_rabotnika', 'lichnaya_kartochka_siz', 'karta_ocenki_riskov', 'instrukciya_po_ohrane_truda']
    list_filter = ['specialnost']
    search_fields = ['specialnost__nazvanie']
    fields = ['specialnost', 'dolzhnostnaya_instrukciya', 'lichnaya_kartochka_rabotnika', 'lichnaya_kartochka_siz', 'karta_ocenki_riskov', 'instrukciya_po_ohrane_truda']


@admin.register(ProtokolyObucheniya)
class ProtokolyObucheniyaAdmin(admin.ModelAdmin):
    list_display = ['shablon_protokola', 'sotrudnik', 'nomer_programmy', 'data_prikaza', 'registracionnyy_nomer', 'raspechatn']
    list_filter = ['data_prikaza', 'raspechatn', 'shablon_protokola']
    search_fields = ['registracionnyy_nomer', 'nomer_programmy', 'shablon_protokola__kurs', 'sotrudnik__fio']


@admin.register(SotrudnikiShablonyProtokolov)
class SotrudnikiShablonyProtokolovAdmin(admin.ModelAdmin):
    list_display = ['kurs', 'html_file']
    list_filter = ['specialnost']
    search_fields = ['kurs']
    fields = ['kurs', 'specialnost', 'html_file']
    filter_horizontal = ['specialnost']
    
    def formfield_for_dbfield(self, db_field, request, **kwargs):
        if db_field.name == 'kurs':
            kwargs['widget'] = admin.widgets.AdminTextareaWidget(attrs={'rows': 4, 'cols': 80})
        return super().formfield_for_dbfield(db_field, request, **kwargs)


@admin.register(Instruktazhi)
class InstruktazhiAdmin(admin.ModelAdmin):
    list_display = ['instruktazh', 'sotrudnik', 'data_provedeniya', 'instruktor']
    list_filter = ['instruktazh__tip_instruktazha', 'instruktazh__specialnost', 'data_provedeniya']
    search_fields = ['instruktazh__specialnost__nazvanie', 'instruktor__fio', 'sotrudnik__fio']
    fields = ['sotrudnik', 'instruktazh', 'data_provedeniya', 'instruktor']


@admin.register(DokumentySotrudnika)
class DokumentySotrudnikaAdmin(admin.ModelAdmin):
    list_display = ['sotrudnik', 'tip_dokumenta', 'sozdano', 'data_sozdaniya']
    list_filter = ['tip_dokumenta', 'sozdano', 'data_sozdaniya']
    search_fields = ['sotrudnik__fio']


@admin.register(ShablonyInstruktazhej)
class ShablonyInstruktazhejAdmin(admin.ModelAdmin):
    list_display = ['specialnost', 'tip_instruktazha', 'html_file']
    list_filter = ['specialnost', 'tip_instruktazha']
    search_fields = ['specialnost__nazvanie']


@admin.register(SotrudnikiZarplaty)
class SotrudnikiZarplatyAdmin(admin.ModelAdmin):
    list_display = ['sotrudnik', 'objekt', 'data', 'kolichestvo_chasov', 'kpi']
    list_filter = ['data', 'objekt', 'sotrudnik__specialnost']
    search_fields = ['sotrudnik__fio', 'objekt__nazvanie']
    date_hierarchy = 'data'