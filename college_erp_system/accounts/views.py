from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.urls import reverse
from .models import User

def login_view(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        
        if user is not None:
            login(request, user)
            # Redirect based on user type
            if user.is_admin:
                return redirect('administration:dashboard')
            elif user.is_teacher:
                return redirect('teachers:dashboard')
            elif user.is_student:
                return redirect('students:dashboard')
        else:
            messages.error(request, 'Invalid username or password.')
    
    return render(request, 'accounts/login.html')

@login_required
def logout_view(request):
    logout(request)
    messages.success(request, 'You have been successfully logged out.')
    return redirect('accounts:login')

@login_required
def profile_view(request):
    return render(request, 'accounts/profile.html', {'user': request.user})

@login_required
def dashboard_redirect(request):
    """Redirect users to their appropriate dashboard based on role"""
    user = request.user
    if user.is_admin:
        return redirect('administration:dashboard')
    elif user.is_teacher:
        return redirect('teachers:dashboard')
    elif user.is_student:
        return redirect('students:dashboard')
    else:
        return redirect('accounts:profile')
