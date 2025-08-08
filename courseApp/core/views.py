from django.shortcuts import render
from core.recommend import recommend_similar_courses
from courses.models import Category, Course
from django.db.models import Count
from django.core.cache import cache

# Create your views here.

def home(request):
    categories = cache.get_or_set("category",lambda: Category.objects.all(),60*5)
    categories_with_courses = []

    if request.user.is_authenticated:
        profile = request.user.profile
        courses = profile.enrolled_courses.all()

        recommend = []
        for i in courses:
            for course, total_score in recommend_similar_courses(i):
                recommend.append((course, total_score))

        sorted_courses = sorted(recommend, key=lambda x: x[1], reverse=True)[:5]
        top_courses = [course.id for course, _ in sorted_courses]
        recommend_courses = Course.objects.filter(id__in=top_courses)

    else:
        recommend_courses = []  


    for category in categories:
        courses = Course.objects.filter(category=category, is_active=True) \
                                .annotate(student_count=Count('enrolled_students')) \
                                .order_by('-student_count')[:5]

        if courses.exists():
            categories_with_courses.append({
                "category": category,
                "courses": courses,
            })

    data = {
        "categories_with_courses": categories_with_courses,
        "slider_courses": Course.objects.filter(is_active=True)[:3],
        "categories_data": categories,
        "recommend_courses":recommend_courses,
    }
    return render(request, 'core/home.html', data)