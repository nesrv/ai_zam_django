from django.urls import path
from . import views
from .views_income import update_income
from .views_totals import get_income_totals

urlpatterns = [
    path('', views.home, name='home'),
    path('objects/', views.objects_list, name='objects_list'),
    path('objects/<int:object_id>/', views.object_detail, name='object_detail'),
    path('objects/<int:object_id>/income/', views.object_income_detail, name='object_income_detail'),

    path('update-expense/', views.update_expense, name='update_expense'),
    path('update-income/', update_income, name='update_income'),
    path('get-income-totals/', get_income_totals, name='get_income_totals'),
    path('update-resource-data/', views.update_resource_data, name='update_resource_data'),
]