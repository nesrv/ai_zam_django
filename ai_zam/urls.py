from django.contrib import admin
from django.urls import path, include, re_path
from django.http import HttpResponse

from django.conf import settings
from django.conf.urls.static import static

from django.views.static import serve as mediaserve

def favicon_view(request):
    return HttpResponse(status=204)

from object.views import home, objects_list, object_detail, object_income_detail, update_expense, update_resource_data
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

    path('update-expense/', update_expense, name='update_expense'),
    path('update-resource-data/', update_resource_data, name='update_resource_data'),
    path('update-income/', update_income, name='update_income'),
    path('get-income-totals/', get_income_totals, name='get_income_totals'),
    path('favicon.ico', favicon_view),
    path('ai/', include('ai.urls')),
    path('telegram/', include('telegrambot.urls')),
    path('sotrudniki/', include('sotrudniki.urls')),
    path('organizations/', organizations_list, name='organizations_main'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    for static_dir in settings.STATICFILES_DIRS:
        urlpatterns += static(settings.STATIC_URL, document_root=static_dir)
else:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    urlpatterns += [
        re_path(f'^{settings.MEDIA_URL.lstrip("/")}(?P<path>.*)$',
            mediaserve, {'document_root': settings.MEDIA_ROOT}),
    ]
