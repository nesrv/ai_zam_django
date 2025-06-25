from django.contrib import admin
from .models import KategoriyaResursa, Resurs, Specialnost, Kadry, Objekt, ResursyPoObjektu

def format_number(value):
    """Форматирует число с пробелами как разделителями разрядов"""
    if value:
        result = int(value)
        return f"{result:,}".replace(',', ' ')
    return '0'

@admin.register(KategoriyaResursa)
class KategoriyaResursaAdmin(admin.ModelAdmin):
    list_display = ('nazvanie',)
    search_fields = ('nazvanie',)

@admin.register(Resurs)
class ResursAdmin(admin.ModelAdmin):
    list_display = ('naimenovanie', 'edinica_izmereniya', 'kategoriya_resursa')
    search_fields = ('naimenovanie',)
    list_filter = ('kategoriya_resursa', 'edinica_izmereniya')

@admin.register(Specialnost)
class SpecialnostAdmin(admin.ModelAdmin):
    list_display = ('nazvanie',)
    search_fields = ('nazvanie',)

@admin.register(Kadry)
class KadryAdmin(admin.ModelAdmin):
    list_display = ('fio', 'specialnost', 'razryad', 'telefon')
    search_fields = ('fio', 'pasport', 'telefon')
    list_filter = ('specialnost', 'razryad')

class ResursyPoObjektuInline(admin.TabularInline):
    model = ResursyPoObjektu
    extra = 1
    fields = ('resurs', 'kolichestvo', 'cena')
    
    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == "resurs":
            kwargs["queryset"] = Resurs.objects.select_related('kategoriya_resursa').order_by('kategoriya_resursa__nazvanie', 'naimenovanie')
        return super().formfield_for_foreignkey(db_field, request, **kwargs)

class KadrovoeObespechenieInline(admin.TabularInline):
    model = ResursyPoObjektu
    extra = 0
    fields = ('resurs', 'kolichestvo', 'cena', 'summa')
    readonly_fields = ('summa',)
    verbose_name = "Кадровое обеспечение"
    verbose_name_plural = "Кадровое обеспечение"
    
    def get_queryset(self, request):
        return super().get_queryset(request).filter(resurs__kategoriya_resursa__nazvanie="Кадровое обеспечение")
    
    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == "resurs":
            kwargs["queryset"] = Resurs.objects.filter(kategoriya_resursa__nazvanie="Кадровое обеспечение")
        return super().formfield_for_foreignkey(db_field, request, **kwargs)
    
    def summa(self, obj):
        if obj.kolichestvo and obj.cena:
            return format_number(obj.kolichestvo * obj.cena)
        return '0'
    summa.short_description = 'Сумма'

class MashinyMekhanizmyInline(admin.TabularInline):
    model = ResursyPoObjektu
    extra = 0
    fields = ('resurs', 'kolichestvo', 'cena', 'summa')
    readonly_fields = ('summa',)
    verbose_name = "Машины и механизмы"
    verbose_name_plural = "Машины и механизмы"
    
    def get_queryset(self, request):
        return super().get_queryset(request).filter(resurs__kategoriya_resursa__nazvanie="Машины и механизмы")
    
    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == "resurs":
            kwargs["queryset"] = Resurs.objects.filter(kategoriya_resursa__nazvanie="Машины и механизмы")
        return super().formfield_for_foreignkey(db_field, request, **kwargs)
    
    def summa(self, obj):
        if obj.kolichestvo and obj.cena:
            return format_number(obj.kolichestvo * obj.cena)
        return '0'
    summa.short_description = 'Сумма'

class InstrumentMaterialyInline(admin.TabularInline):
    model = ResursyPoObjektu
    extra = 0
    fields = ('resurs', 'kolichestvo', 'cena', 'summa')
    readonly_fields = ('summa',)
    verbose_name = "Инструмент и материалы"
    verbose_name_plural = "Инструмент и материалы"
    
    def get_queryset(self, request):
        return super().get_queryset(request).filter(resurs__kategoriya_resursa__nazvanie="Инструмент и материалы")
    
    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == "resurs":
            kwargs["queryset"] = Resurs.objects.filter(kategoriya_resursa__nazvanie="Инструмент и материалы")
        return super().formfield_for_foreignkey(db_field, request, **kwargs)
    
    def summa(self, obj):
        if obj.kolichestvo and obj.cena:
            return format_number(obj.kolichestvo * obj.cena)
        return '0'
    summa.short_description = 'Сумма'

class ABRInline(admin.TabularInline):
    model = ResursyPoObjektu
    extra = 0
    fields = ('resurs', 'kolichestvo', 'cena', 'summa')
    readonly_fields = ('summa',)
    verbose_name = "Административно бытовые расходы"
    verbose_name_plural = "Административно бытовые расходы"
    
    def get_queryset(self, request):
        return super().get_queryset(request).filter(resurs__kategoriya_resursa__nazvanie="Административно бытовые расходы")
    
    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == "resurs":
            kwargs["queryset"] = Resurs.objects.filter(kategoriya_resursa__nazvanie="Административно бытовые расходы")
        return super().formfield_for_foreignkey(db_field, request, **kwargs)
    
    def summa(self, obj):
        if obj.kolichestvo and obj.cena:
            return format_number(obj.kolichestvo * obj.cena)
        return '0'
    summa.short_description = 'Сумма'

class SIZInline(admin.TabularInline):
    model = ResursyPoObjektu
    extra = 0
    fields = ('resurs', 'kolichestvo', 'cena', 'summa')
    readonly_fields = ('summa',)
    verbose_name = "СИЗ спецодежда"
    verbose_name_plural = "СИЗ спецодежда"
    
    def get_queryset(self, request):
        return super().get_queryset(request).filter(resurs__kategoriya_resursa__nazvanie="СИЗ спецодежда")
    
    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == "resurs":
            kwargs["queryset"] = Resurs.objects.filter(kategoriya_resursa__nazvanie="СИЗ спецодежда")
        return super().formfield_for_foreignkey(db_field, request, **kwargs)
    
    def summa(self, obj):
        if obj.kolichestvo and obj.cena:
            return format_number(obj.kolichestvo * obj.cena)
        return '0'
    summa.short_description = 'Сумма'

class PodryadchikiInline(admin.TabularInline):
    model = ResursyPoObjektu
    extra = 0
    fields = ('resurs', 'kolichestvo', 'cena', 'summa')
    readonly_fields = ('summa',)
    verbose_name = "Подрядные организации"
    verbose_name_plural = "Подрядные организации"
    
    def get_queryset(self, request):
        return super().get_queryset(request).filter(resurs__kategoriya_resursa__nazvanie="Подрядные организации")
    
    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == "resurs":
            kwargs["queryset"] = Resurs.objects.filter(kategoriya_resursa__nazvanie="Подрядные организации")
        return super().formfield_for_foreignkey(db_field, request, **kwargs)
    
    def summa(self, obj):
        if obj.kolichestvo and obj.cena:
            return format_number(obj.kolichestvo * obj.cena)
        return '0'
    summa.short_description = 'Сумма'

@admin.register(Objekt)
class ObjektAdmin(admin.ModelAdmin):
    list_display = ('nazvanie', 'otvetstvennyj', 'data_nachala', 'data_plan_zaversheniya', 'status')
    search_fields = ('nazvanie',)
    list_filter = ('status', 'data_nachala', 'otvetstvennyj')
    date_hierarchy = 'data_nachala'
    inlines = [KadrovoeObespechenieInline, MashinyMekhanizmyInline, InstrumentMaterialyInline, ABRInline, SIZInline, PodryadchikiInline]
    fieldsets = (
        (None, {
            'fields': ('nazvanie', 'otvetstvennyj', 'status')
        }),
        ('Даты', {
            'fields': ('data_nachala', 'data_plan_zaversheniya', 'data_fakt_zaversheniya')
        }),
    )

@admin.register(ResursyPoObjektu)
class ResursyPoObjektuAdmin(admin.ModelAdmin):
    list_display = ('objekt', 'resurs', 'kolichestvo', 'cena')
    search_fields = ('objekt__nazvanie', 'resurs__naimenovanie')
    list_filter = ('resurs__kategoriya_resursa',)