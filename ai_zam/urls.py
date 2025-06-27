from django.contrib import admin
from django.urls import path, include, re_path

from django.conf import settings
from django.conf.urls.static import static

from django.views.static import serve as mediaserve

from object.views import home, objects_list, object_detail, update_expense, update_resource_data

# Изменяем заголовки админки
admin.site.site_header = "Ruslan administration"
admin.site.site_title = "Ruslan administration"
admin.site.index_title = "Добро пожаловать в Ruslan administration"

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', home, name='home'),
    path('objects/', objects_list, name='objects_list'),
    path('objects/<int:object_id>/', object_detail, name='object_detail'),
    path('update-expense/', update_expense, name='update_expense'),
    path('update-resource-data/', update_resource_data, name='update_resource_data'),
    path('ai/', include('ai.urls')),
    path('telegram/', include('telegrambot.urls')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    # Добавляем обработку статических файлов из STATICFILES_DIRS
    for static_dir in settings.STATICFILES_DIRS:
        urlpatterns += static(settings.STATIC_URL, document_root=static_dir)

else:
    urlpatterns += [
        re_path(f'^{settings.MEDIA_URL.lstrip("/")}(?P<path>.*)$',
            mediaserve, {'document_root': settings.MEDIA_ROOT}),
        re_path(f'^{settings.STATIC_URL.lstrip("/")}(?P<path>.*)$',
            mediaserve, {'document_root': settings.STATIC_ROOT}),
    ]
