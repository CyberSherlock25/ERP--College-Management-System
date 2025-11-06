from django.urls import path
from django.shortcuts import render
from . import views

app_name = 'teachers'

def placeholder_view(request):
    return render(request, 'teachers/placeholder.html')

urlpatterns = [
    path('dashboard/', views.dashboard, name='dashboard'),
    path('timetable/', views.teacher_timetable, name='timetable'),
    path('attendance/', views.attendance_select, name='attendance'),
    path('attendance/<int:subject_id>/', views.attendance_mark, name='attendance_mark'),
    path('exams/', views.exam_select, name='exam_select'),
    path('exams/schedule/', views.schedule_exam, name='schedule_exam'),
    path('grades/', views.enter_grades, name='enter_grades'),
    path('classes/', views.my_classes, name='my_classes'),
]
