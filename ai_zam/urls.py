from django.contrib import admin
from django.urls import path, include, re_path
from django.http import HttpResponse

from django.conf import settings
from django.conf.urls.static import static

from django.views.static import serve as mediaserve
from django.views.static import serve as staticserve

def favicon_view(request):
    return HttpResponse(status=204)

from object.views import home
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
]

# Обслуживание статических файлов
urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

if settings.DEBUG:
    for static_dir in settings.STATICFILES_DIRS:
        urlpatterns += static(settings.STATIC_URL, document_root=static_dir)