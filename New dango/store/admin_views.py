
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.models import User
from django.contrib import messages

def admin_add_admin(request):
    if not request.user.is_superuser:
        messages.error(request, "Access denied. Superuser privileges required.")
        return redirect('store_admin')
        
    if request.method == 'POST':
        username = request.POST.get('username')
        email = request.POST.get('email')
        password = request.POST.get('password')
        role = request.POST.get('role') # 'admin' or 'superadmin'
        
        if User.objects.filter(username=username).exists():
            messages.error(request, "Username already exists.")
            return redirect('store_admin')
            
        user = User.objects.create_user(username=username, email=email, password=password)
        user.is_staff = True
        if role == 'superadmin':
            user.is_superuser = True
        user.save()
        messages.success(request, f"Admin '{username}' added successfully.")
        return redirect('store_admin')
    return redirect('store_admin')

def admin_delete_admin(request, user_id):
    if not request.user.is_superuser:
        messages.error(request, "Access denied. Superuser privileges required.")
        return redirect('store_admin')
        
    user = get_object_or_404(User, pk=user_id)
    if user.is_superuser and User.objects.filter(is_superuser=True).count() <= 1:
        messages.error(request, "Cannot delete the last superuser.")
        return redirect('store_admin')
        
    if user == request.user:
        messages.error(request, "You cannot delete yourself.")
        return redirect('store_admin')
        
    user.delete()
    messages.success(request, f"Admin '{user.username}' deleted successfully.")
    return redirect('store_admin')
