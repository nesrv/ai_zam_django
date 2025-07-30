from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.models import User
from django import forms
from .models import KategoriyaResursa, Resurs, Objekt, ResursyPoObjektu, FakticheskijResursPoObjektu, RaskhodResursa, DokhodResursa, SvodnayaRaskhodDokhodPoDnyam, UserProfile

def format_number(value):
    """Форматирует число с пробелами как разделителями разрядов"""
    if value:
        result = int(value)
        return f"{result:,}".replace(',', ' ')
    return '0'

@admin.register(KategoriyaResursa)
class KategoriyaResursaAdmin(admin.ModelAdmin):
    list_display = ('nazvanie', 'raskhod_dokhod', 'order')
    list_editable = ('raskhod_dokhod', 'order')
    search_fields = ('nazvanie',)
    ordering = ('order',)
    
    def delete_model(self, request, obj):
        # Удаляем все связанные записи
        from django.db import transaction
        with transaction.atomic():
            resursy = Resurs.objects.filter(kategoriya_resursa=obj)
            for resurs in resursy:
                # Удаляем фактические ресурсы
                FakticheskijResursPoObjektu.objects.filter(resurs_po_objektu__resurs=resurs).delete()
                # Удаляем ресурсы по объекту
                ResursyPoObjektu.objects.filter(resurs=resurs).delete()
            # Удаляем ресурсы
            resursy.delete()
            # Удаляем категорию
            obj.delete()
    
    def delete_queryset(self, request, queryset):
        for obj in queryset:
            self.delete_model(request, obj)

@admin.register(Resurs)
class ResursAdmin(admin.ModelAdmin):
    list_display = ('naimenovanie', 'edinica_izmereniya', 'kategoriya_resursa')
    search_fields = ('naimenovanie',)
    list_filter = ('kategoriya_resursa', 'edinica_izmereniya')



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
    list_display = ('nazvanie', 'otvetstvennyj', 'data_nachala', 'data_plan_zaversheniya', 'status', 'is_active')
    search_fields = ('nazvanie',)
    list_filter = ('status', 'data_nachala', 'otvetstvennyj', 'is_active')
    date_hierarchy = 'data_nachala'
    inlines = [KadrovoeObespechenieInline, MashinyMekhanizmyInline, InstrumentMaterialyInline, ABRInline, SIZInline, PodryadchikiInline]
    filter_horizontal = ['sotrudniki', 'organizacii']
    actions = ['deactivate_objects', 'activate_objects']
    fieldsets = (
        (None, {
            'fields': ('nazvanie', 'otvetstvennyj', 'status', 'is_active')
        }),
        ('Даты', {
            'fields': ('data_nachala', 'data_plan_zaversheniya', 'data_fakt_zaversheniya')
        }),
        ('Связи', {
            'fields': ('organizacii', 'sotrudniki')
        }),
    )
    
    def deactivate_objects(self, request, queryset):
        updated = queryset.update(is_active=False)
        self.message_user(request, f'{updated} объект(ов) деактивировано.')
    deactivate_objects.short_description = "Деактивировать выбранные объекты"
    
    def activate_objects(self, request, queryset):
        updated = queryset.update(is_active=True)
        self.message_user(request, f'{updated} объект(ов) активировано.')
    activate_objects.short_description = "Активировать выбранные объекты"
    
    def has_delete_permission(self, request, obj=None):
        # Разрешаем полное удаление объектов через админку
        return True
    
    def delete_queryset(self, request, queryset):
        # Переопределяем удаление для корректной обработки связанных записей
        for obj in queryset:
            # Удаляем связанные записи
            ResursyPoObjektu.objects.filter(objekt=obj).delete()
            SvodnayaRaskhodDokhodPoDnyam.objects.filter(objekt=obj).delete()
        # Удаляем сами объекты
        queryset.delete()
    
    def fakticheskiye_raskhody_display(self, obj):
        if not obj.id:
            return "Нет данных"
        
        fakticheskiye_raskhody = RaskhodResursa.objects.filter(
            fakticheskij_resurs__resurs_po_objektu__objekt_id=obj.id
        ).select_related(
            'fakticheskij_resurs__resurs_po_objektu__resurs'
        ).order_by('-data')[:10]
        
        if not fakticheskiye_raskhody.exists():
            return "Нет фактических расходов"
        
        html = '<table>'
        html += '<tr>'
        html += '<th>Ресурс</th>'
        html += '<th>Дата</th>'
        html += '<th>Израсходовано</th>'
        html += '</tr>'
        
        for raskhod in fakticheskiye_raskhody:
            html += '<tr>'
            html += f'<td>{raskhod.fakticheskij_resurs.resurs_po_objektu.resurs.naimenovanie}</td>'
            html += f'<td>{raskhod.data.strftime("%d.%m.%Y")}</td>'
            html += f'<td>{format_number(raskhod.izraskhodovano)}</td>'
            html += '</tr>'
        
        html += '</table>'
        
        from django.utils.safestring import mark_safe
        return mark_safe(html)
    
    fakticheskiye_raskhody_display.short_description = 'Последние 10 дней'
    
    def change_view(self, request, object_id, form_url='', extra_context=None):
        extra_context = extra_context or {}
        if object_id:
            fakticheskiye_raskhody = RaskhodResursa.objects.filter(
                fakticheskij_resurs__resurs_po_objektu__objekt_id=object_id
            ).select_related(
                'fakticheskij_resurs__resurs_po_objektu__resurs'
            ).order_by('-data')[:10]
            
            # Создаем HTML таблицу
            if fakticheskiye_raskhody.exists():
                table_html = '<div>'
                table_html += '<h2>Фактические расходы ресурсов (последние 10 дней)</h2>'
                table_html += '<table>'
                table_html += '<tr>'
                table_html += '<th>Ресурс</th>'
                table_html += '<th>Дата</th>'
                table_html += '<th>Израсходовано</th>'
                table_html += '</tr>'
                
                for raskhod in fakticheskiye_raskhody:
                    table_html += '<tr>'
                    table_html += f'<td>{raskhod.fakticheskij_resurs.resurs_po_objektu.resurs.naimenovanie}</td>'
                    table_html += f'<td>{raskhod.data.strftime("%d.%m.%Y")}</td>'
                    table_html += f'<td>{int(raskhod.izraskhodovano)}</td>'
                    table_html += '</tr>'
                
                table_html += '</table></div>'
                
                # Добавляем HTML в контекст
                from django.utils.safestring import mark_safe
                extra_context['raskhody_table'] = mark_safe(table_html)
        
        return super().change_view(request, object_id, form_url, extra_context)

@admin.register(ResursyPoObjektu)
class ResursyPoObjektuAdmin(admin.ModelAdmin):
    list_display = ('objekt', 'resurs', 'kolichestvo', 'cena')
    search_fields = ('objekt__nazvanie', 'resurs__naimenovanie')
    list_filter = ('resurs__kategoriya_resursa',)

class RaskhodResursaInline(admin.TabularInline):
    model = RaskhodResursa
    extra = 1
    fields = ('data', 'izraskhodovano')



class FakticheskijResursForm(forms.ModelForm):
    objekt = forms.ModelChoiceField(
        queryset=Objekt.objects.all(),
        empty_label="Выберите объект",
        required=False,
        label="Объект"
    )
    
    class Meta:
        model = FakticheskijResursPoObjektu
        fields = '__all__'
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if 'objekt' in self.data:
            try:
                objekt_id = int(self.data.get('objekt'))
                self.fields['resurs_po_objektu'].queryset = ResursyPoObjektu.objects.filter(objekt_id=objekt_id)
            except (ValueError, TypeError):
                pass
        elif self.instance.pk:
            self.fields['objekt'].initial = self.instance.resurs_po_objektu.objekt
            self.fields['resurs_po_objektu'].queryset = ResursyPoObjektu.objects.filter(
                objekt=self.instance.resurs_po_objektu.objekt
            )
        else:
            self.fields['resurs_po_objektu'].queryset = ResursyPoObjektu.objects.all()

@admin.register(FakticheskijResursPoObjektu)
class FakticheskijResursPoObjektuAdmin(admin.ModelAdmin):
    form = FakticheskijResursForm
    list_display = ('resurs_po_objektu', 'get_objekt', 'get_resurs')
    search_fields = ('resurs_po_objektu__objekt__nazvanie', 'resurs_po_objektu__resurs__naimenovanie')
    list_filter = ('resurs_po_objektu__objekt', 'resurs_po_objektu__resurs__kategoriya_resursa')
    inlines = [RaskhodResursaInline]
    fieldsets = (
        (None, {
            'fields': ('objekt', 'resurs_po_objektu')
        }),
    )
    
    def get_objekt(self, obj):
        return obj.resurs_po_objektu.objekt.nazvanie
    get_objekt.short_description = 'Объект'
    
    def get_resurs(self, obj):
        return obj.resurs_po_objektu.resurs.naimenovanie
    get_resurs.short_description = 'Ресурс'
    
    class Media:
        js = ('admin/js/fakticheskij_resurs.js',)

@admin.register(RaskhodResursa)
class RaskhodResursaAdmin(admin.ModelAdmin):
    list_display = ('fakticheskij_resurs', 'data', 'izraskhodovano')
    search_fields = ('fakticheskij_resurs__resurs_po_objektu__objekt__nazvanie',)
    list_filter = ('data',)
    date_hierarchy = 'data'

@admin.register(DokhodResursa)
class DokhodResursaAdmin(admin.ModelAdmin):
    list_display = ('fakticheskij_resurs', 'data', 'vypolneno')
    search_fields = ('fakticheskij_resurs__resurs_po_objektu__objekt__nazvanie',)
    list_filter = ('data',)
    date_hierarchy = 'data'

@admin.register(SvodnayaRaskhodDokhodPoDnyam)
class SvodnayaRaskhodDokhodPoDnyamAdmin(admin.ModelAdmin):
    list_display = ('objekt', 'data', 'raskhod', 'dokhod', 'balans')
    search_fields = ('objekt__nazvanie',)
    list_filter = ('objekt', 'data')
    date_hierarchy = 'data'
    readonly_fields = ('balans',)
    ordering = ('-data',)
    
    def changelist_view(self, request, extra_context=None):
        extra_context = extra_context or {}
        extra_context['title'] = 'Выберите объект для просмотра сводной информации'
        return super().changelist_view(request, extra_context)
class UserProfileInline(admin.StackedInline):
    model = UserProfile
    can_delete = False
    verbose_name_plural = 'Профиль'

class UserAdmin(BaseUserAdmin):
    inlines = (UserProfileInline,)

admin.site.unregister(User)
admin.site.register(User, UserAdmin)
class UserProfileInline(admin.StackedInline):
    model = UserProfile
    can_delete = False
    verbose_name_plural = 'Профиль'
    filter_horizontal = ['organizations']

class UserAdmin(BaseUserAdmin):
    inlines = (UserProfileInline,)

admin.site.unregister(User)
admin.site.register(User, UserAdmin)