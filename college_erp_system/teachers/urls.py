from django.urls import path
from django.shortcuts import render

app_name = 'teachers'

def placeholder_view(request):
    return render(request, 'teachers/placeholder.html')

urlpatterns = [
    path('dashboard/', placeholder_view, name='dashboard'),
    path('timetable/', placeholder_view, name='timetable'),
    path('attendance/', placeholder_view, name='attendance'),
    path('exams/', placeholder_view, name='exams'),
    path('grades/', placeholder_view, name='grades'),
    path('classes/', placeholder_view, name='classes'),
]
