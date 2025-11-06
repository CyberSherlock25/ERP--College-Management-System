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
    
    # Financial Management URLs
    path('fees/management/', views.fee_management, name='fee_management'),
    path('fees/bulk-assign/', views.bulk_assign_fees, name='bulk_assign_fees'),
    path('fees/search-students-api/', views.search_students_api, name='search_students_api'),
    path('fees/payment-methods/', views.manage_payment_methods, name='manage_payment_methods'),
    path('fees/fee-structure/', views.fee_structure_management, name='fee_structure_management'),
    path('fees/transactions/', views.transaction_history, name='transaction_history'),
    path('fees/student/<int:student_id>/', views.student_fee_details, name='student_fee_details'),
    path('fees/process-payment/', views.process_payment, name='process_payment'),
    path('fees/reports/', views.financial_reports, name='financial_reports'),
]
