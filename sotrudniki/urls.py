from django.urls import path
from . import views

app_name = 'sotrudniki'

urlpatterns = [
    path('organizations/', views.organizations_list, name='organizations'),
    path('organization/<int:pk>/', views.organization_detail, name='organization_detail'),
    path('update-status/', views.update_document_status, name='update_status'),
    path('<int:pk>/', views.sotrudnik_detail, name='detail'),
    path('', views.sotrudniki_list, name='list'),
]