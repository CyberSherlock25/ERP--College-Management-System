from django.contrib import admin
from .models import Teacher

@admin.register(Teacher)
class TeacherAdmin(admin.ModelAdmin):
    list_display = ['employee_id', 'user', 'department', 'designation', 'employment_type', 'is_active']
    list_filter = ['department', 'designation', 'employment_type', 'qualification', 'is_active']
    search_fields = ['employee_id', 'user__first_name', 'user__last_name', 'designation']
    date_hierarchy = 'joining_date'
