from django.urls import path
from . import views

app_name = 'students'

urlpatterns = [
    path('dashboard/', views.dashboard, name='dashboard'),
    path('timetable/', views.timetable, name='timetable'),
    path('attendance/', views.attendance, name='attendance'),
    path('exams/', views.exams, name='exams'),
    path('results/', views.results, name='results'),
    path('fees/', views.fees, name='fees'),
    path('notifications/', views.notifications, name='notifications'),
    path('academic-calendar/', views.academic_calendar, name='academic_calendar'),
]
