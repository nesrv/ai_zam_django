from django.urls import path
from . import views
from . import views_edit
from . import views_income
from . import views_totals
from . import export_views
from . import api_views
from . import api

urlpatterns = [
    path('', views.home, name='home'),
    path('objects/', views.objects_list, name='objects_list'),
    path('objects/<int:object_id>/', views.object_detail, name='object_detail'),
    path('objects/<int:object_id>/income/', views.object_income_detail, name='object_income_detail'),
    path('objects/<int:object_id>/edit/', views_edit.edit_object, name='edit_object'),
    path('objects/<int:object_id>/delete/', views.delete_object, name='delete_object'),
    path('objects/create/', views.create_object, name='create_object'),
    path('objects/<int:object_id>/employees/', api_views.get_employees_by_object_position, name='get_employees_by_position'),
    path('objects/<int:object_id>/debug-employees/', views.debug_employees, name='debug_employees'),
    path('update-expense/', views.update_expense, name='update_expense'),
    path('update-resource-data/', views.update_resource_data, name='update_resource_data'),
    path('add-category/', views.add_category, name='add_category'),
    path('add-resource/', views.add_resource, name='add_resource'),
    path('add-category-to-object/', views.add_category_to_object, name='add_category_to_object'),
    path('add-employee-ajax/', views.add_employee_ajax, name='add_employee_ajax'),
    path('add-resource-to-object/', views.add_resource_to_object, name='add_resource_to_object'),
    path('delete-resource-from-object/', views.delete_resource_from_object, name='delete_resource_from_object'),
    path('get-resources-by-category/<int:category_id>/', views.get_resources_by_category, name='get_resources_by_category'),
    path('get-employees-by-resource/<int:resource_id>/', views.get_employees_by_resource, name='get_employees_by_resource'),
    path('objects/<int:object_id>/api/employees-by-object-position/', views.get_employees_by_object_position, name='get_employees_by_object_position'),

    path('api/check-employee/<int:object_id>/<int:employee_id>/', views.check_employee_in_object, name='check_employee_in_object'),
    path('api/add-employee-to-object/<int:object_id>/<int:employee_id>/', views.add_employee_to_object_api, name='add_employee_to_object_api'),
    
    # Экспорт
    path('objects/<int:object_id>/export/excel/', export_views.export_object_to_excel, name='export_object_to_excel'),
    path('objects/<int:object_id>/export/pdf/', export_views.export_object_to_pdf, name='export_object_to_pdf'),
    
    # Сводные данные
    path('objects/<int:object_id>/totals/', views_totals.object_totals, name='object_totals'),
]