from django.urls import path
from . import views

app_name = 'cams'

urlpatterns = [
    path('', views.camera_list, name='camera_list'),
]