from django.shortcuts import render
from courses.models import Category, Course

# Create your views here.

def home(request):
    course_data = Course.objects.all()
    categories_data = Category.objects.all()
    data = {"categories_data": categories_data, "course_data": course_data}
    return render(request, 'core/home.html',data)

def contact(request):
    return render(request, 'core/contact.html')