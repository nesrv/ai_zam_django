from django.contrib import admin
from .models import (
    Organizaciya, Podrazdelenie, Specialnost, Sotrudnik, DokumentySotrudnika,
    InstrukciiKartochki, ProtokolyObucheniya, Instruktazhi, VidyDokumentov, ShablonDolzhnostnojInstrukcii,
    ShablonyDokumentovPoSpecialnosti
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
    fields = ['dolzhnostnaya_instrukciya', 'lichnaya_kartochka_rabotnika', 'lichnaya_kartochka_siz', 'karta_ocenki_riskov']


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
    inlines = [InstrukciiKartochkiInline, ProtokolyObucheniyaInline, InstruktazhiInline]


@admin.register(Sotrudnik)
class SotrudnikAdmin(admin.ModelAdmin):
    list_display = ['fio', 'organizaciya', 'specialnost', 'podrazdelenie', 'data_priema', 'data_nachala_raboty']
    list_filter = ['organizaciya', 'specialnost', 'podrazdelenie', 'data_priema']
    search_fields = ['fio']
    date_hierarchy = 'data_priema'


@admin.register(InstrukciiKartochki)
class InstrukciiKartochkiAdmin(admin.ModelAdmin):
    list_display = ['nazvanie', 'dokumenty_sotrudnika', 'soglasovan', 'raspechatn', 'data_sozdaniya']
    list_filter = ['soglasovan', 'raspechatn', 'data_sozdaniya']
    search_fields = ['nazvanie']
    fields = ['dokumenty_sotrudnika', 'nazvanie', 'shablon_instrukcii', 'soglasovan', 'raspechatn']


@admin.register(ProtokolyObucheniya)
class ProtokolyObucheniyaAdmin(admin.ModelAdmin):
    list_display = ['nomer_programmy', 'nazvanie_kursa', 'dokumenty_sotrudnika', 'data_prikaza', 'raspechatn']
    list_filter = ['data_prikaza', 'raspechatn']
    search_fields = ['nomer_programmy', 'nazvanie_kursa']


@admin.register(Instruktazhi)
class InstruktazhiAdmin(admin.ModelAdmin):
    list_display = ['vid_instruktazha', 'dokumenty_sotrudnika', 'data_instruktazha', 'instruktor', 'raspechatn']
    list_filter = ['vid_instruktazha', 'data_instruktazha', 'raspechatn']
    search_fields = ['vid_instruktazha', 'instruktor']


@admin.register(VidyDokumentov)
class VidyDokumentovAdmin(admin.ModelAdmin):
    list_display = ['nazvanie', 'tip']
    list_filter = ['tip']
    search_fields = ['nazvanie']


@admin.register(ShablonDolzhnostnojInstrukcii)
class ShablonDolzhnostnojInstrukciiAdmin(admin.ModelAdmin):
    list_display = ['name', 'created_at', 'updated_at']
    search_fields = ['name']
    readonly_fields = ['created_at', 'updated_at']


@admin.register(ShablonyDokumentovPoSpecialnosti)
class ShablonyDokumentovPoSpecialnostiAdmin(admin.ModelAdmin):
    list_display = ['specialnost', 'dolzhnostnaya_instrukciya', 'lichnaya_kartochka_rabotnika', 'lichnaya_kartochka_siz', 'karta_ocenki_riskov']
    list_filter = ['specialnost']
    search_fields = ['specialnost__nazvanie']
    fields = ['specialnost', 'dolzhnostnaya_instrukciya', 'lichnaya_kartochka_rabotnika', 'lichnaya_kartochka_siz', 'karta_ocenki_riskov']