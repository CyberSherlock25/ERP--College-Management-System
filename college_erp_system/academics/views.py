from django.shortcuts import render

# Create your views here.
def index(request):
    login = request.user
    College_name = "MIT World Peace University"

    welcome_message = "Welcome to the ERP System"
    login.username = "Rival"
    login.is_authenticated: True
    user_role = "Administrator"

    return render(request, 'index.html', {'login': login, 'College_name': College_name, 'welcome_message': welcome_message, 'user_role': user_role, 'admin': True, 'user_permissions': ['add_user', 'delete_user', 'view_reports']})
