from django.urls import path
from . import views

app_name = 'sotrudniki'

urlpatterns = [
    path('organizations/', views.organizations_list, name='organizations'),
    path('organization/<int:pk>/', views.organization_detail, name='organization_detail'),
    path('organization/<int:pk>/delete/', views.delete_organization, name='delete_organization'),
    path('add/', views.sotrudnik_add, name='add'),
    path('update-status/', views.update_document_status, name='update_status'),
    path('generate-documents/', views.generate_documents, name='generate_documents'),
    path('<int:sotrudnik_id>/download/<str:doc_type>/', views.download_document, name='download_document'),
    path('<int:sotrudnik_id>/download/<str:doc_type>/<int:protokol_id>/', views.download_document, name='download_protokol'),
    path('<int:pk>/documents/', views.sotrudnik_documents, name='documents'),
    path('<int:pk>/editor/<str:doc_type>/', views.document_editor, name='document_editor'),
    path('<int:pk>/edit/<str:doc_type>/', views.document_edit, name='document_edit'),
    path('<int:pk>/', views.sotrudnik_detail, name='detail'),
    path('salary/<int:sotrudnik_id>/', views.sotrudnik_salary, name='sotrudnik_salary'),
    path('get-stavka/<int:objekt_id>/<int:sotrudnik_id>/', views.get_stavka, name='get_stavka'),
    path('save-salary/', views.save_salary, name='save_salary'),
    path('update-vydano/', views.update_vydano, name='update_vydano'),
    path('salaries/', views.salaries_list, name='salaries_list'),
    path('control/', views.control_list, name='control'),
    path('update-control-status/', views.update_control_status, name='update_control_status'),
    path('', views.sotrudniki_list, name='list'),
]