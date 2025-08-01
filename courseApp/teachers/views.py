from django.shortcuts import get_object_or_404, redirect, render
from django.http import HttpResponse
from django.urls import reverse
from courses.models import Category, Course
from account.models import Profile
from django.core.paginator import Paginator ,EmptyPage, PageNotAnInteger
from .form.course_edit import course_control
from django.contrib.auth.decorators import user_passes_test
from django.contrib import messages


def login(user):
    return user.is_authenticated

def is_teacher(user):
    return user.groups.filter(name='Teacher').exists()


def home(request):
    categories = Category.objects.all()
    categories_with_courses = []

    for category in categories:
        courses = Course.objects.filter(category=category, is_active=True)
        if courses.exists():
            categories_with_courses.append({
                "category": category,
                "courses": courses,
            })

    data = {
        "categories_with_courses": categories_with_courses,
        "slider_courses": Course.objects.filter(is_active=True)[:3],
        "categories_data": categories,
    }
    return render(request, 'core/home.html', data)

def teacher_details(request,id):
    courses = Course.objects.filter(teacher = id).all()
    teacher = get_object_or_404(Profile, user__id=id, is_teacher=True)
    
    return render(request, 'teachers/teacher_details.html', {"teacher": teacher,"courses":courses})

@user_passes_test(is_teacher)
def create_course(request):
    if request.method == "POST":
        form = course_control(request.POST, request.FILES)
        if form.is_valid(): 
            if form.warning:
                messages.warning(request, form.warning)
            course = form.save(commit=False)  
            course.teacher = request.user    
            course.save()  
            return redirect("teacher_courses")
        else:
            messages.error(request,"hata oldu")
            return render(request, "courses/create_courses.html", {"form": form})

            
    else:
        form = course_control()
    return render(request, "courses/create_course.html", {"form": form})

@user_passes_test(is_teacher) 
def edit_course(request,id):
    course = get_object_or_404(Course,pk = id)
    if  course.teacher != request.user:
        messages.error(request, "You do not have permission to edit this course.")
        return redirect("student_courses")
        
    if request.method == "POST":
        form = course_control(request.POST, request.FILES, instance=course) 
        if form.is_valid():
            if form.warning:
                messages.warning(request, form.warning)
            form.save()
            messages.success(request, "Success")
            return redirect("teacher_courses")
        else:
            messages.error(request, "error")
            return redirect("student_courses")
    else:
        
        form = course_control(instance=course)
    
    return render(request, "courses/create_course.html", {"form": form})

@user_passes_test(is_teacher)
def delete_course(request,id):
    course = get_object_or_404(Course,pk = id)
    if  course.teacher != request.user:
        messages.error(request, "You do not have permission to delete this course.")
        referer = request.META.get('HTTP_REFERER')
        if referer:
            return redirect(referer)
        else:
            return redirect("my_courses")
        
    if request.method == "POST":
        course.delete()
        return redirect("my_courses")


    return render(request, "courses/delete_course.html", {"course": course})

@user_passes_test(is_teacher)
def teacher_courses(request):
    categories_data = Category.objects.all()
    courses = Course.objects.filter(teacher=request.user)

    page = Paginator(courses, 10)  # Sayfa başına 2 kurs göster
    page_number = request.GET.get('page', 1)

    try:
        page_obj = page.page(page_number)
    except PageNotAnInteger:
        # Sayfa sayısı integer değilse, ilk sayfayı göster
        page_obj = page.page(1)
    except EmptyPage:
        # Sayfa yoksa, son sayfayı göster
        page_obj = page.page(page.num_pages)

    context = {
        "page_obj": page_obj,
        "categories_data": categories_data,  
    }
    return render(request, 'courses/admin_courses.html',context)
