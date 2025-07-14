from django.urls import path
from . import views

app_name = 'analytics'

urlpatterns = [
    path('', views.analytics_home, name='home'),
    path('daily-expenses/', views.daily_expenses_analytics, name='daily_expenses'),
    path('risk-prediction/', views.risk_prediction, name='risk_prediction'),
    path('schedule-analysis/', views.schedule_analysis, name='schedule_analysis'),
    path('task-recommendations/', views.task_recommendations, name='task_recommendations'),
    path('deadline-risks/', views.deadline_risks, name='deadline_risks'),
    path('efficiency-analysis/', views.efficiency_analysis, name='efficiency_analysis'),
    path('legal-risks/', views.legal_risks, name='legal_risks'),
]