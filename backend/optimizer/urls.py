from django.urls import path

from . import views

app_name = 'optimizer'

urlpatterns = [
    path('recommendations/', views.recommendations_view, name='recommendations'),
    path('budget/set/', views.set_budget_view, name='budget_set'),
    path('budget/status/', views.budget_status_view, name='budget_status'),
    path('budget/alerts/check/', views.budget_alert_check_view, name='budget_alert_check'),
    path('scheduler/set/', views.scheduler_set_view, name='scheduler_set'),
    path('scheduler/list/', views.scheduler_list_view, name='scheduler_list'),
    path('scheduler/<int:schedule_id>/toggle/', views.scheduler_toggle_view, name='scheduler_toggle'),
    path('simulator/', views.simulator_view, name='simulator'),
    path('carbon/', views.carbon_view, name='carbon'),
    path('sustainability/', views.sustainability_view, name='sustainability'),
    path('region-advisor/', views.region_advisor_view, name='region_advisor'),
    path('kubernetes/simulate/', views.kubernetes_simulation_view, name='kubernetes_simulate'),
    path('chatbot/', views.chatbot_view, name='chatbot'),
]
