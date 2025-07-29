from django.shortcuts import redirect, render
from django.contrib.auth import authenticate,login,logout
from django.contrib.auth.models import User
from django.contrib import messages
from django.contrib.auth.models import User
from django.shortcuts import render, redirect


# Create your views here.

def user_login(request):
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
        user_username = request.POST.get("username")
        user_email = request.POST.get("email")
        user_password = request.POST.get("password")
        user_repassword = request.POST.get("repassword")

        if user_password != user_repassword:
            messages.error(request, "Passwords do not match")

            return render(request, "account/register.html")

        if User.objects.filter(username=user_username).exists():
            messages.error(request, "This username is already taken")

            return render(request, "account/register.html")

        if User.objects.filter(email=user_email).exists():
            messages.error(request, "This email is already registered")

            return render(request, "account/register.html")

        # Güvenli şekilde kullanıcı oluştur
        User.objects.create_user(username=user_username, email=user_email, password=user_password)
        messages.success(request, "User created successfully!")
        return redirect("user_login")
    
    return render(request, "account/register.html")



def user_logout(request):
    logout(request)
    return redirect("home")
    
