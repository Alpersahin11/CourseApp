from django.shortcuts import get_object_or_404, redirect, render
from django.http import HttpResponse
from django.urls import reverse
from .models import Category, Course
from django.core.paginator import Paginator ,EmptyPage, PageNotAnInteger
from .form.course_edit import course_control
from django.contrib.auth.decorators import user_passes_test



def home(request):
    course_data = Course.objects.all()
    categories_data = Category.objects.all()
    data = {"categories_data": categories_data, "course_data": course_data}
    return render(request, 'home.html',data)

def course(request):
    course_name = request.GET.get("q","")
    categories_data = Category.objects.all()
    courses = Course.objects.filter(title__contains = course_name)
    page = Paginator(courses, 2)  # Sayfa başına 2 kurs göster
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
    return render(request, 'courses/course.html',context)

def source_course(request):
 
    course_name = request.GET.get("q","")
    categories_data = Category.objects.all()
    courses = Course.objects.filter(title__contains = course_name)

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
    return render(request, 'courses/course.html',context)

def login(user):
    return user.is_superuser

@user_passes_test(login)
def create_course(request):
    if request.method == "POST":
        form = course_control(request.POST, request.FILES)
        if form.is_valid():  # VALIDASYONU KONTROL ET
            form.save()
            return redirect("my_courses")
        else:
            print(form.errors)  # Hataları konsola yazdır (geliştirme için)
    else:
        form = course_control()
    return render(request, "courses/create_course.html", {"form": form})

@user_passes_test(login)
def edit_course(request,id):
    course = get_object_or_404(Course,pk = id)

    if request.method == "POST":
        form = course_control(request.POST , instance=course)
        form.save()
        return redirect("my_courses")
    else:
        form = course_control(instance=course)
    
    return render(request, "courses/create_course.html", {"form": form})

@user_passes_test(login)
def delete_course(request,id):

    course = get_object_or_404(Course,pk = id)
    if request.method == "POST":
        course.delete()
        return redirect("my_courses")


    return render(request, "courses/delete_course.html", {"course": course})

@user_passes_test(login)
def my_course(request):
    categories_data = Category.objects.all()
    courses = Course.objects.filter()

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

def contact(request):
    return render(request, 'contact.html')

def course_details(request, id):
    categories_data = Category.objects.all()
    course_data = Course.objects.all()

    course = [course for course in course_data if course.tag == id]
    if course:
        return render(request, 'courses/course_details.html', {"course": course[0],"alone":True})
    else:
        return HttpResponse("Course not found", status=404)

def course_details_id(request, id):
    course_data = Course.objects.all()

    course = [course for course in course_data if course.id == id]
    if len(course)>0:
        reverse_url = reverse("course_details", kwargs={"id": course[0].tag})
    
        return redirect(reverse_url)
    else:
        return HttpResponse("Course not found", status=404)

def categorie(request, id):

    course_name = request.GET.get("q","")

    categories_data = Category.objects.all()

    category = Category.objects.filter(tag=id).first()

    if not category:
        return HttpResponse("Category not found", status=404)
    
    courses = Course.objects.filter(category=category, is_active=True,title__contains = course_name)

    page = Paginator(courses, 2)  
    page_number = request.GET.get('page',1)

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



    return render(request, 'courses/course.html', context)

    
