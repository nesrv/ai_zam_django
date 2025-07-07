from django.contrib import admin
from django.urls import path, include, re_path
from django.http import HttpResponse

from django.conf import settings
from django.conf.urls.static import static

from django.views.static import serve as mediaserve
from django.views.static import serve as staticserve

def favicon_view(request):
    return HttpResponse(status=204)

from object.views import home, objects_list, object_detail, object_income_detail, create_object, update_expense, update_resource_data, add_category, add_resource, add_category_to_object
from object.views_income import update_income
from object.views_totals import get_income_totals
from sotrudniki.views import organizations_list

# Изменяем заголовки админки
# admin.site.site_header = "Ruslan administration"
# admin.site.site_title = "Ruslan administration"
# admin.site.index_title = "Добро пожаловать в Ruslan administration"

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', home, name='home'),
    path('objects/', objects_list, name='objects_list'),
    path('objects/<int:object_id>/', object_detail, name='object_detail'),
    path('objects/<int:object_id>/income/', object_income_detail, name='object_income_detail'),
    path('objects/create/', create_object, name='create_object'),

    path('update-expense/', update_expense, name='update_expense'),
    path('update-resource-data/', update_resource_data, name='update_resource_data'),
    path('update-income/', update_income, name='update_income'),
    path('get-income-totals/', get_income_totals, name='get_income_totals'),
    path('add-category/', add_category, name='add_category'),
    path('add-resource/', add_resource, name='add_resource'),
    path('add-category-to-object/', add_category_to_object, name='add_category_to_object'),
    path('favicon.ico', favicon_view),
    path('ai/', include('ai.urls')),
    path('telegram/', include('telegrambot.urls')),
    path('sotrudniki/', include('sotrudniki.urls')),
    path('kadry/', organizations_list, name='organizations_main'),
]

# Обслуживание статических файлов
urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

if settings.DEBUG:
    for static_dir in settings.STATICFILES_DIRS:
        urlpatterns += static(settings.STATIC_URL, document_root=static_dir)
