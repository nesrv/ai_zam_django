from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('objects/', views.objects_list, name='objects_list'),
    path('objects/<int:object_id>/', views.object_detail, name='object_detail'),
    path('objects/<int:object_id>/income/', views.object_income_detail, name='object_income_detail'),
    path('update-expense/', views.update_expense, name='update_expense'),
    path('update-resource-data/', views.update_resource_data, name='update_resource_data'),
]