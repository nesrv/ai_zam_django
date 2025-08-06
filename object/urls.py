from django.urls import path
from . import views
from . import views_edit
from . import views_income
from . import views_totals
from . import export_views
from . import api_views
from . import api
from . import debug_views

urlpatterns = [
    path('', views.objects_list, name='objects_list'),
    path('<int:object_id>/', views.object_detail, name='object_detail'),
    path('<int:object_id>/income/', views.object_income_detail, name='object_income_detail'),

    path('<int:object_id>/edit/', views_edit.edit_object, name='edit_object'),
    path('<int:object_id>/update-name/', views_edit.update_object_name, name='update_object_name'),
    path('<int:object_id>/update-date/', views_edit.update_object_date, name='update_object_date'),
    path('<int:object_id>/delete/', views.delete_object, name='delete_object'),
    path('<int:object_id>/add-chat/', views.add_chat_to_object, name='add_chat_to_object'),
    path('create/', views.create_object, name='create_object'),
    path('<int:object_id>/employees/', api_views.get_employees_simple, name='get_employees_by_position'),
    path('<int:object_id>/debug-employees/', views.debug_employees, name='debug_employees'),
    path('<int:object_id>/debug-cell/', api_views.debug_cell_info, name='debug_cell_info'),
    path('<int:object_id>/debug-salary/', debug_views.debug_salary_data, name='debug_salary_data'),
    path('<int:object_id>/get-salary-data/', api_views.get_salary_data, name='get_salary_data'),
    path('<int:object_id>/export/', export_views.export_object_json, name='export_object_json'),
    path('<int:object_id>/save-hours/', views.save_employee_hours, name='save_employee_hours'),
    path('<int:object_id>/api/employees-by-object-position/', views.get_employees_by_object_position, name='get_employees_by_object_position'),
    
    # API
    path('api/check-employee/<int:object_id>/<int:employee_id>/', views.check_employee_in_object, name='check_employee_in_object'),
    path('api/add-employee-to-object/<int:object_id>/<int:employee_id>/', views.add_employee_to_object_api, name='add_employee_to_object_api'),
    path('update-expense/', views.update_expense, name='update_expense'),
    path('update-resource-data/', views.update_resource_data, name='update_resource_data'),
    path('update-income/', views_income.update_income, name='update_income'),
    path('get-income-totals/', views_totals.get_income_totals, name='get_income_totals'),
    path('add-category/', views.add_category, name='add_category'),
    path('add-resource/', views.add_resource, name='add_resource'),
    path('add-category-to-object/', views.add_category_to_object, name='add_category_to_object'),
    path('add-employee-ajax/', views.add_employee_ajax, name='add_employee_ajax'),
    path('add-resource-to-object/', views.add_resource_to_object, name='add_resource_to_object'),
    path('delete-resource-from-object/', views.delete_resource_from_object, name='delete_resource_from_object'),
    path('get-resources-by-category/<int:category_id>/', views.get_resources_by_category, name='get_resources_by_category'),
    path('get-resources/<int:category_id>/', views.get_resources_by_category, name='get_resources'),
    path('get-employees-by-resource/<int:resource_id>/', views.get_employees_by_resource, name='get_employees_by_resource'),
    
    # Профиль и аутентификация
    path('profile/', views.profile, name='profile'),
    path('demo-profile/', views.demo_profile, name='demo_profile'),
    path('add-bot/', views.add_bot, name='add_bot'),
    path('get-chat-ids/', views.get_chat_ids, name='get_chat_ids'),
    path('save-chat-to-objects/', views.save_chat_to_objects, name='save_chat_to_objects'),
    path('remove-chat-from-objects/', views.remove_chat_from_objects, name='remove_chat_from_objects'),
    path('register/', views.register, name='register'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
]