from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('objects/', views.objects_list, name='objects_list'),
    path('objects/<int:object_id>/', views.object_detail, name='object_detail'),
    path('update-expense/', views.update_expense, name='update_expense'),
]