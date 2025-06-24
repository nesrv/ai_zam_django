from django.contrib import admin
from .models import SpecodezhaSiz

@admin.register(SpecodezhaSiz)
class SpecodezhaSizAdmin(admin.ModelAdmin):
    list_display = ('nazvanie', 'edinica_izmereniya')
    search_fields = ('nazvanie',)
    list_filter = ('edinica_izmereniya',)
