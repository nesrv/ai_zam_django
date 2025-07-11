from django.urls import path
from . import views
from .views_income import update_income
from .views_totals import get_income_totals
from .views_edit import edit_object

urlpatterns = [
    path('', views.home, name='home'),
    path('objects/', views.objects_list, name='objects_list'),
    path('objects/<int:object_id>/', views.object_detail, name='object_detail'),
    path('objects/create/', views.create_object, name='create_object'),
    path('objects/<int:object_id>/income/', views.object_income_detail, name='object_income_detail'),

    path('update-expense/', views.update_expense, name='update_expense'),
    path('update-income/', update_income, name='update_income'),
    path('get-income-totals/', get_income_totals, name='get_income_totals'),
    path('update-resource-data/', views.update_resource_data, name='update_resource_data'),
    path('add-employee-ajax/', views.add_employee_ajax, name='add_employee_ajax'),
    path('get-resources/<int:category_id>/', views.get_resources_by_category, name='get_resources_by_category'),
    path('get-employees/<int:resource_id>/', views.get_employees_by_resource, name='get_employees_by_resource'),
    path('objects/<int:object_id>/edit/', edit_object, name='edit_object'),
]