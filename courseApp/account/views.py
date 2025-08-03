from django.shortcuts import redirect, render
from django.contrib.auth import authenticate,login,logout
from django.contrib import messages
from django.shortcuts import render, redirect
from django.urls import reverse
from django.contrib.auth.models import Group
from account.forms import CustomPasswordChangeForm, ProfileForm, UserForm,UserEditForm
from .models import Profile 
from django.contrib.auth.decorators import login_required
from django.contrib.auth import update_session_auth_hash
from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth.hashers import make_password
from django.shortcuts import render, redirect
from django.contrib import messages
from .forms import UserForm
from .models import Profile 

def user_login(request):

    if request.user.is_authenticated:
        return redirect("edit_profile")

    if request.method == "POST":
        
        user_username = request.POST.get("username")
        user_password = request.POST.get("password") 

        user = authenticate(request,username = user_username,password = user_password)

        if user is not None:
            login(request,user)
            messages.success(request, "Success")
            return redirect("home")
        else:
            messages.error(request, "Username or password is not correct.")
            return render(request, "account/login.html")
        
    return render(request,"account/login.html")

def user_register(request):
    if request.method == "POST":
        user_form = UserForm(request.POST)

        if user_form.is_valid():
            user = user_form.save(commit=False)
            user.password = make_password(user_form.cleaned_data['password'])
            user.save()

            Profile.objects.create(user=user)

            student_group, created = Group.objects.get_or_create(name="Student")
            user.groups.add(student_group)

            messages.success(request, "User created successfully!")
            return redirect("edit_profile")
        else:
            messages.error(request, "Please correct the errors below.")
    else:
        user_form = UserForm()

    return render(request, "account/register.html", {"form": user_form})

@login_required
def edit_profile(request):
    user = request.user
    try:
        profile = user.profile
    except Profile.DoesNotExist:
        profile = Profile.objects.create(user=user)

    active_tab = request.GET.get('tab', 'account-general')
    user_form = UserEditForm(instance=user)
    profile_form = ProfileForm(instance=profile)
    password_form = CustomPasswordChangeForm(user=request.user)

    if request.method == 'POST':
        active_tab = request.POST.get('active_tab', 'account-general') 

        if active_tab == 'account-general':
            user_form = UserEditForm(request.POST, instance=user)
            profile_form = ProfileForm(request.POST, request.FILES, instance=profile)

            if user_form.is_valid() and profile_form.is_valid():
                user_form.save()
                profile_form.save()
                messages.success(request, "Profile information updated successfully!")
                return redirect(f"{reverse('edit_profile')}?tab=account-general")
            else:
                messages.error(request, "Please fix the errors in the General Settings section.")

        elif active_tab == 'account-change-password':
            password_form = CustomPasswordChangeForm(user, request.POST)
            if password_form.is_valid():
                user = password_form.save()
                update_session_auth_hash(request, user)
                messages.success(request, "Password changed successfully!")
                return redirect(f"{reverse('edit_profile')}?tab=account-change-password")
            else:
                messages.error(request, "Please fix the errors in the Password Change section.")

        elif active_tab == 'account-info' and profile.is_teacher:
            profile_form = ProfileForm(request.POST, request.FILES, instance=profile)

            if profile_form.is_valid():
                profile_form.save()
                messages.success(request, "Additional information updated successfully!")
                return redirect(f"{reverse('edit_profile')}?tab=account-info")
            else:
                messages.error(request, "Please fix the errors in the Additional Info section.")

    context = {
        'user_form': user_form,
        'profile_form': profile_form,
        'password_form': password_form,
        'active_tab': active_tab,
        'profile': profile
    }

    return render(request, 'account/edit_profile.html', context)

@login_required
def become_instructor(request):
    user = request.user
    profile = user.profile

    # Profil güncelle
    profile.is_teacher = True
    profile.save()

    # Grup kontrolü ve ekleme
    teacher_group, created = Group.objects.get_or_create(name="Teacher")
    user.groups.add(teacher_group)

    messages.success(request, "You are now an instructor!")
    return redirect('edit_profile')


def user_logout(request):
    logout(request)
    return redirect("home")
    
