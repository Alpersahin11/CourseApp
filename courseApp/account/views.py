from django.shortcuts import redirect, render
from django.contrib.auth import authenticate,login,logout
from django.contrib.auth.models import User
from django.contrib import messages
from django.contrib.auth.models import User
from django.shortcuts import render, redirect
from django.urls import reverse

from account.forms import CustomPasswordChangeForm, ProfileForm, UserForm,UserEditForm
from .models import Profile 
from django.core.exceptions import ObjectDoesNotExist
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import PasswordChangeForm
from django.contrib.auth import update_session_auth_hash
from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth.models import User
from django.contrib.auth.hashers import make_password
from django.shortcuts import render, redirect
from django.contrib import messages
from .forms import UserForm
from .models import Profile 

def user_login(request):

    if request.user.is_authenticated:
        return redirect("edit_profil")

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
            # Şifreyi hash'le
            user = user_form.save(commit=False)
            user.password = make_password(user_form.cleaned_data['password'])
            user.save()

            # Profil oluştur (eğer varsa)
            Profile.objects.create(user=user)

            messages.success(request, "User created successfully!")
            return redirect("user_login")
        else:
            messages.error(request, "Form is invalid.")
    else:
        user_form = UserForm()

    return render(request, "account/register.html", {"form": user_form})


@login_required
def edit_profil(request):
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
        active_tab = request.POST.get('active_tab', 'account-general')  # formdan gelen sekme bilgisi

        if active_tab == 'account-general':
            user_form = UserEditForm(request.POST, instance=user)
            profile_form = ProfileForm(request.POST, request.FILES, instance=profile)

            if user_form.is_valid() and profile_form.is_valid():
                user_form.save()
                profile_form.save()
                messages.success(request, "Profil bilgileri başarıyla güncellendi!")
                return redirect(f"{reverse('edit_profil')}?tab=account-general")
            else:
                messages.error(request, "Lütfen Genel Ayarlar bölümündeki hataları düzeltin.")

        elif active_tab == 'account-change-password':
            password_form = PasswordChangeForm(user, request.POST)
            if password_form.is_valid():
                user = password_form.save()
                update_session_auth_hash(request, user)
                messages.success(request, "Şifre başarıyla değiştirildi!")
                return redirect(f"{reverse('edit_profil')}?tab=account-change-password")
            else:
                messages.error(request, "Lütfen Şifre Değiştirme bölümündeki hataları düzeltin.")

        elif active_tab == 'account-info':
            profile_form = ProfileForm(request.POST, request.FILES, instance=profile)

            if profile_form.is_valid():
                profile_form.save()
                messages.success(request, "Ek bilgiler başarıyla güncellendi!")
                return redirect(f"{reverse('edit_profil')}?tab=account-info")
            else:
                messages.error(request, "Lütfen Bilgi bölümündeki hataları düzeltin.")

    context = {
        'user_form': user_form,
        'profile_form': profile_form,
        'password_form': password_form,
        'active_tab': active_tab,
        'profile':profile
    }

    return render(request, 'account/edit_profil.html', context)


def user_logout(request):
    logout(request)
    return redirect("home")
    
