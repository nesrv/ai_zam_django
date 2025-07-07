from django.contrib import admin
from .models import (
    Organizaciya, Podrazdelenie, Specialnost, Sotrudnik, DokumentySotrudnika,
    InstrukciiKartochki, ProtokolyObucheniya, Instruktazhi,
    ShablonyDokumentovPoSpecialnosti, SotrudnikiShablonyProtokolov
)


@admin.register(Organizaciya)
class OrganizaciyaAdmin(admin.ModelAdmin):
    list_display = ['nazvanie', 'inn']
    search_fields = ['nazvanie', 'inn']


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
    list_display = ['nazvanie']
    search_fields = ['nazvanie']
    inlines = [ShablonyDokumentovPoSpecialnostiInline]


class InstrukciiKartochkiInline(admin.TabularInline):
    model = InstrukciiKartochki
    extra = 0


class ProtokolyObucheniyaInline(admin.TabularInline):
    model = ProtokolyObucheniya
    extra = 0


class InstruktazhiInline(admin.TabularInline):
    model = Instruktazhi
    extra = 0


@admin.register(DokumentySotrudnika)
class DokumentySotrudnikaAdmin(admin.ModelAdmin):
    list_display = ['sotrudnik']
    inlines = [InstrukciiKartochkiInline, InstruktazhiInline]


@admin.register(Sotrudnik)
class SotrudnikAdmin(admin.ModelAdmin):
    list_display = ['fio', 'organizaciya', 'specialnost', 'podrazdelenie', 'data_priema', 'data_nachala_raboty']
    list_filter = ['organizaciya', 'specialnost', 'podrazdelenie', 'data_priema']
    search_fields = ['fio']
    date_hierarchy = 'data_priema'
    inlines = [ProtokolyObucheniyaInline]


@admin.register(InstrukciiKartochki)
class InstrukciiKartochkiAdmin(admin.ModelAdmin):
    list_display = ['nazvanie', 'dokumenty_sotrudnika', 'soglasovan', 'raspechatn', 'data_sozdaniya']
    list_filter = ['soglasovan', 'raspechatn', 'data_sozdaniya']
    search_fields = ['nazvanie']
    fields = ['dokumenty_sotrudnika', 'nazvanie', 'shablon_instrukcii', 'soglasovan', 'raspechatn']


@admin.register(Instruktazhi)
class InstruktazhiAdmin(admin.ModelAdmin):
    list_display = ['vid_instruktazha', 'dokumenty_sotrudnika', 'data_instruktazha', 'instruktor', 'raspechatn']
    list_filter = ['vid_instruktazha', 'data_instruktazha', 'raspechatn']
    search_fields = ['vid_instruktazha', 'instruktor']



@admin.register(ShablonyDokumentovPoSpecialnosti)
class ShablonyDokumentovPoSpecialnostiAdmin(admin.ModelAdmin):
    list_display = ['specialnost', 'dolzhnostnaya_instrukciya', 'lichnaya_kartochka_rabotnika', 'lichnaya_kartochka_siz', 'karta_ocenki_riskov', 'instrukciya_po_ohrane_truda']
    list_filter = ['specialnost']
    search_fields = ['specialnost__nazvanie']
    fields = ['specialnost', 'dolzhnostnaya_instrukciya', 'lichnaya_kartochka_rabotnika', 'lichnaya_kartochka_siz', 'karta_ocenki_riskov', 'instrukciya_po_ohrane_truda']


@admin.register(ProtokolyObucheniya)
class ProtokolyObucheniyaAdmin(admin.ModelAdmin):
    list_display = ['shablon_protokola', 'sotrudnik', 'data_prikaza', 'registracionnyy_nomer', 'raspechatn']
    list_filter = ['data_prikaza', 'raspechatn']
    search_fields = ['registracionnyy_nomer', 'shablon_protokola__nomer_programmy', 'shablon_protokola__kurs', 'sotrudnik__fio']


@admin.register(SotrudnikiShablonyProtokolov)
class SotrudnikiShablonyProtokolovAdmin(admin.ModelAdmin):
    list_display = ['nomer_programmy', 'kurs', 'html_file']
    list_filter = ['nomer_programmy']
    search_fields = ['nomer_programmy', 'kurs']
    fields = ['nomer_programmy', 'kurs', 'html_file']