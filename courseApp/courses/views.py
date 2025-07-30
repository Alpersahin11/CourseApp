from django.shortcuts import get_object_or_404, redirect, render
from django.http import HttpResponse
from django.urls import reverse
from .models import Category, Course
from django.core.paginator import Paginator ,EmptyPage, PageNotAnInteger
from .form.course_edit import course_control
from django.contrib.auth.decorators import user_passes_test
from django.contrib import messages


def login(user):
    return user.is_authenticated

def is_teacher(user):
    return user.groups.filter(name='Teacher').exists()




def course(request):
    course_name = request.GET.get("q","")
    categories_data = Category.objects.all()
    courses = Course.objects.filter(title__contains = course_name)
    page = Paginator(courses, 9)  # Sayfa başına 2 kurs göster
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

@user_passes_test(login)
def student_courses(request):
    categories_data = Category.objects.all()
    profile = request.user.profile
    courses = profile.enrolled_courses.all()

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
    return render(request, 'courses/study_courses.html',context)

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

    page = Paginator(courses, 9)  
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

def enroll_course(request, id):
    if not request.user.is_authenticated:
        return redirect("user_login")

    course = get_object_or_404(Course, pk=id)

    if course.teacher == request.user:
        messages.error(request, "Kendi kursunuza kayıt olamazsınız.")
        return redirect("course_details", id=course.id)

    if course in request.user.profile.enrolled_courses.all():
        messages.info(request, "Zaten bu kursa kayıtlısınız.")
    else:
        request.user.profile.enrolled_courses.add(course)
        messages.success(request, "Kursa başarıyla kayıt oldunuz.")

    return redirect("course_details", id=course.id)


    
