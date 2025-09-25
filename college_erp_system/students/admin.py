from django.contrib import admin
from .models import Student, Notification

@admin.register(Student)
class StudentAdmin(admin.ModelAdmin):
    list_display = ['roll_number', 'admission_number', 'user', 'department', 'student_class', 'is_active']
    list_filter = ['department', 'student_class', 'is_active', 'admission_date']
    search_fields = ['roll_number', 'admission_number', 'user__first_name', 'user__last_name']
    date_hierarchy = 'admission_date'

@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = ['title', 'notification_type', 'target_audience', 'is_urgent', 'created_by', 'created_at']
    list_filter = ['notification_type', 'target_audience', 'is_urgent', 'created_at']
    search_fields = ['title', 'message']
    date_hierarchy = 'created_at'
