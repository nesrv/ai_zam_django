from django.contrib import admin
from .models import SpecodezhaSiz, AdministrativnoBytovyeRashody, InstrumentMaterialy, MashinyMekhanizmy, KadrovoeObespechenie, PodryadnyeOrganizacii, Specialnost, Kadry

@admin.register(SpecodezhaSiz)
class SpecodezhaSizAdmin(admin.ModelAdmin):
    list_display = ('nazvanie', 'edinica_izmereniya')
    search_fields = ('nazvanie',)
    list_filter = ('edinica_izmereniya',)

@admin.register(AdministrativnoBytovyeRashody)
class AdministrativnoBytovyeRashodyAdmin(admin.ModelAdmin):
    list_display = ('nazvanie', 'edinica_izmereniya')
    search_fields = ('nazvanie',)
    list_filter = ('edinica_izmereniya',)

@admin.register(InstrumentMaterialy)
class InstrumentMaterialyAdmin(admin.ModelAdmin):
    list_display = ('nazvanie', 'edinica_izmereniya')
    search_fields = ('nazvanie',)
    list_filter = ('edinica_izmereniya',)

@admin.register(MashinyMekhanizmy)
class MashinyMekhanizmyAdmin(admin.ModelAdmin):
    list_display = ('nazvanie', 'edinica_izmereniya')
    search_fields = ('nazvanie',)
    list_filter = ('edinica_izmereniya',)

@admin.register(KadrovoeObespechenie)
class KadrovoeObespecenieAdmin(admin.ModelAdmin):
    list_display = ('naimenovanie', 'edinica_izmereniya')
    search_fields = ('naimenovanie',)
    list_filter = ('edinica_izmereniya',)

@admin.register(PodryadnyeOrganizacii)
class PodryadnyeOrganizaciiAdmin(admin.ModelAdmin):
    list_display = ('naimenovanie', 'edinica_izmereniya')
    search_fields = ('naimenovanie',)
    list_filter = ('edinica_izmereniya',)

@admin.register(Specialnost)
class SpecialnostAdmin(admin.ModelAdmin):
    list_display = ('nazvanie',)
    search_fields = ('nazvanie',)

@admin.register(Kadry)
class KadryAdmin(admin.ModelAdmin):
    list_display = ('fio', 'specialnost', 'razryad', 'telefon')
    search_fields = ('fio', 'pasport', 'telefon')
    list_filter = ('specialnost', 'razryad')
