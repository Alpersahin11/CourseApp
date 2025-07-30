from django.shortcuts import render
from courses.models import Category, Course

# Create your views here.

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