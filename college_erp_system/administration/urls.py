from django.urls import path
from . import views

app_name = 'administration'

urlpatterns = [
    path('dashboard/', views.dashboard, name='dashboard'),
    path('analytics/', views.get_dashboard_analytics, name='analytics'),
    path('notifications/send/', views.send_notification, name='send_notification'),
    path('notice/send/', views.send_notice, name='send_notice'),
    path('reports/', views.system_reports, name='reports'),
    path('users/', views.manage_users, name='users'),
    path('get-user/<int:user_id>/', views.get_user_data, name='get_user_data'),
    path('edit-user/', views.edit_user, name='edit_user'),
    path('add-student/', views.add_student, name='add_student'),
    path('add-teacher/', views.add_teacher, name='add_teacher'),
    path('department/<int:dept_id>/', views.department_details, name='department_details'),
    path('quick-actions/', views.quick_actions, name='quick_actions'),
    path('export/', views.export_data, name='export_data'),
    path('attendance/', views.attendance_overview, name='attendance_overview'),
    path('financial/', views.financial_dashboard, name='financial_dashboard'),
    path('academic-performance/', views.academic_performance, name='academic_performance'),
]
