from django.contrib import admin
from django.urls import path, include, re_path
from django.http import HttpResponse
from django.shortcuts import redirect

from django.conf import settings
from django.conf.urls.static import static

from django.views.static import serve as mediaserve
from django.views.static import serve as staticserve

def favicon_view(request):
    from django.http import FileResponse
    import os
    # Сначала пробуем STATIC_ROOT (для продакшена)
    favicon_path = os.path.join(settings.STATIC_ROOT, 'favicon.ico')
    if not os.path.exists(favicon_path):
        # Если не найден, пробуем STATICFILES_DIRS (для разработки)
        favicon_path = os.path.join(settings.BASE_DIR, 'static', 'favicon.ico')
    try:
        return FileResponse(open(favicon_path, 'rb'), content_type='image/x-icon')
    except FileNotFoundError:
        return HttpResponse(status=404)

from object.views import home, get_resources_by_category, add_resource_to_object, delete_resource_from_object
from sotrudniki.views import organizations_list
from telegrambot import views


# Изменяем заголовки админки
# admin.site.site_header = "Ruslan administration"
# admin.site.site_title = "Ruslan administration"
# admin.site.index_title = "Добро пожаловать в Ruslan administration"

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', home, name='home'),
    path('favicon.ico', favicon_view),
    path('ai/', include('ai.urls')),
    path('telegram/', include('telegrambot.urls')),
    path('ai-agent/', views.bot_status, name='ai_agent'),
    path('sotrudniki/', include('sotrudniki.urls')),
    path('kadry/', organizations_list, name='organizations_main'),
    path('analytics/', include('analytics.urls')),
    path('cameras/', include('cams.urls')),
    path('objects/', include('object.urls')),
    path('get-resources/<int:category_id>/', get_resources_by_category, name='get_resources'),
    path('get-resources-by-category/<int:category_id>/', get_resources_by_category, name='get_resources_by_category'),
    path('add-resource-to-object/', add_resource_to_object, name='add_resource_to_object'),
    path('delete-resource-from-object/', delete_resource_from_object, name='delete_resource_from_object'),
    path('organizations/', lambda request: redirect('/kadry/'), name='organizations_redirect'),

]

# Обслуживание статических файлов
urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

if settings.DEBUG:
    for static_dir in settings.STATICFILES_DIRS:
        urlpatterns += static(settings.STATIC_URL, document_root=static_dir)