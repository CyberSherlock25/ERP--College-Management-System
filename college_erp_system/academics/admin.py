from django.contrib import admin
from .models import (
    Department, Course, Class, Subject, TimeSlot, 
    Timetable, Attendance, Exam, Result, Fee,
    AcademicCalendar, TeacherTimetable
)

@admin.register(Department)
class DepartmentAdmin(admin.ModelAdmin):
    list_display = ['name', 'code', 'head', 'created_at']
    search_fields = ['name', 'code']
    list_filter = ['created_at']

@admin.register(Course)
class CourseAdmin(admin.ModelAdmin):
    list_display = ['code', 'name', 'department', 'semester', 'credits']
    list_filter = ['department', 'semester', 'credits']
    search_fields = ['name', 'code']

@admin.register(Class)
class ClassAdmin(admin.ModelAdmin):
    list_display = ['name', 'department', 'semester', 'section', 'academic_year', 'class_teacher']
    list_filter = ['department', 'semester', 'academic_year']
    search_fields = ['name', 'section']

@admin.register(Subject)
class SubjectAdmin(admin.ModelAdmin):
    list_display = ['course', 'class_assigned', 'teacher']
    list_filter = ['course__department', 'class_assigned__semester']
    search_fields = ['course__name', 'course__code']

@admin.register(TimeSlot)
class TimeSlotAdmin(admin.ModelAdmin):
    list_display = ['day', 'start_time', 'end_time']
    list_filter = ['day']
    ordering = ['day', 'start_time']

@admin.register(Timetable)
class TimetableAdmin(admin.ModelAdmin):
    list_display = ['class_assigned', 'subject', 'time_slot', 'room_number']
    list_filter = ['class_assigned__department', 'time_slot__day']
    search_fields = ['subject__course__name', 'room_number']

@admin.register(Attendance)
class AttendanceAdmin(admin.ModelAdmin):
    list_display = ['student', 'subject', 'date', 'is_present', 'marked_by']
    list_filter = ['date', 'is_present', 'subject__course__department']
    search_fields = ['student__username', 'subject__course__name']
    date_hierarchy = 'date'

@admin.register(Exam)
class ExamAdmin(admin.ModelAdmin):
    list_display = ['name', 'exam_type', 'subject', 'date', 'total_marks', 'created_by']
    list_filter = ['exam_type', 'subject__course__department', 'date']
    search_fields = ['name', 'subject__course__name']
    date_hierarchy = 'date'

@admin.register(Result)
class ResultAdmin(admin.ModelAdmin):
    list_display = ['student', 'exam', 'marks_obtained', 'grade', 'is_published']
    list_filter = ['grade', 'is_published', 'exam__exam_type']
    search_fields = ['student__username', 'exam__name']
    list_editable = ['is_published']

@admin.register(Fee)
class FeeAdmin(admin.ModelAdmin):
    list_display = ['student', 'fee_type', 'amount', 'due_date', 'payment_status', 'payment_date']
    list_filter = ['fee_type', 'payment_status', 'academic_year', 'semester']
    search_fields = ['student__username', 'transaction_id']
    date_hierarchy = 'due_date'
    list_editable = ['payment_status']

@admin.register(AcademicCalendar)
class AcademicCalendarAdmin(admin.ModelAdmin):
    list_display = ['title', 'category', 'start_date', 'end_date', 'academic_year', 'instructional_days', 'working_days']
    list_filter = ['category', 'academic_year', 'start_date']
    search_fields = ['title', 'remarks']
    date_hierarchy = 'start_date'
    list_editable = ['instructional_days', 'working_days']

@admin.register(TeacherTimetable)
class TeacherTimetableAdmin(admin.ModelAdmin):
    list_display = ['teacher', 'subject', 'time_slot', 'room_number', 'academic_year']
    list_filter = ['academic_year', 'time_slot__day', 'teacher']
    search_fields = ['teacher__username', 'teacher__first_name', 'teacher__last_name', 'subject__course__name', 'room_number']
    ordering = ['time_slot__day', 'time_slot__start_time']
