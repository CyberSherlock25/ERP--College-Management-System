from django.urls import path
from django.shortcuts import render

app_name = 'administration'

def placeholder_view(request):
    return render(request, 'administration/placeholder.html')

urlpatterns = [
    path('dashboard/', placeholder_view, name='dashboard'),
    path('users/', placeholder_view, name='users'),
    path('reports/', placeholder_view, name='reports'),
]
