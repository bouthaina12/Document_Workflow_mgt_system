from django.contrib.auth import login, authenticate
from django.shortcuts import render, redirect
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseForbidden
from django.contrib.auth.models import Group, User


# Register view
def register(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
             # Add the user to the 'Employees' group by default
            employees_group = Group.objects.get(name='Employees')
            user.groups.add(employees_group)
            return redirect('login')
    else:
        form = UserCreationForm()
    return render(request, 'accounts/register.html', {'form': form})

# Login view
def login_view(request):
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            # Redirect based on role
            if user.groups.filter(name='Administrators').exists():
                return redirect('admin_view')
            elif user.groups.filter(name='Employees').exists():
                return redirect('/documents/')  # Redirect to document list or creation form
            else:
                return HttpResponseForbidden("You do not have permission to access this page.")
    else:
        form = AuthenticationForm()
    return render(request, 'accounts/login.html', {'form': form})

# Group-required decorator
def group_required(group_name):
    def decorator(view_func):
        def wrapper(request, *args, **kwargs):
            if not request.user.is_authenticated:
                return redirect('login')
            if not request.user.groups.filter(name=group_name).exists():
                return HttpResponseForbidden("You do not have permission to access this page.")
            return view_func(request, *args, **kwargs)
        return wrapper
    return decorator

# Admin-only view
@login_required
@group_required('Administrators')
def admin_view(request):
    return render(request, 'accounts/admin_page.html')
