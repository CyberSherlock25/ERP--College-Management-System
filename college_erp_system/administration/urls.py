from django.urls import path
from . import views

app_name = 'administration'

urlpatterns = [
    path('dashboard/', views.dashboard, name='dashboard'),
    path('analytics/', views.get_dashboard_analytics, name='analytics'),
    path('notifications/send/', views.send_notification, name='send_notification'),
    path('reports/', views.system_reports, name='reports'),
    path('users/', views.manage_users, name='users'),
    path('department/<int:dept_id>/', views.department_details, name='department_details'),
    path('quick-actions/', views.quick_actions, name='quick_actions'),
    path('export/', views.export_data, name='export_data'),
    path('attendance/', views.attendance_overview, name='attendance_overview'),
    path('financial/', views.financial_dashboard, name='financial_dashboard'),
    path('academic-performance/', views.academic_performance, name='academic_performance'),
]
