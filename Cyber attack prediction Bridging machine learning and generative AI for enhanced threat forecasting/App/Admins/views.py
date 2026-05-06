from django.shortcuts import render, redirect
from django.contrib.auth.models import User
from django.contrib import messages
from Users.models import PredictionRecord

def adminhome(request):
    users = User.objects.filter(is_staff=False, is_superuser=False) 
    return render(request, "Admin/adminhome.html", {"users": users})

def admin_update_userstatus(request, user_id):
    try:
        user = User.objects.get(id=user_id)
        
        # Toggle the is_active status
        user.is_active = not user.is_active
        user.save()

        # Display message based on the action
        if user.is_active:
            messages.success(request, f"User {user.username} has been activated.")
        else:
            messages.success(request, f"User {user.username} has been deactivated.")
        
        return redirect('adminhome')  # Redirect back to the admin home page
    except User.DoesNotExist:
        messages.error(request, "User not found.")
        return redirect('adminhome')
    
def reports(request):
    records = PredictionRecord.objects.filter().order_by("-created_at")
    return render(request, "Admin/reports.html", {"records": records})
    
def adminproposed(request):
    return render(request, "Admin/proposed.html")