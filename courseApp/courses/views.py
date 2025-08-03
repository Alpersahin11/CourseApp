import json
from django.shortcuts import get_object_or_404, redirect, render
from django.http import HttpResponse
from django.urls import reverse

from core.recommend import recommend_similar_courses
from .models import Category, Course
from account.models import Enrollment, Profile 
from django.core.paginator import Paginator ,EmptyPage, PageNotAnInteger
from django.contrib.auth.decorators import user_passes_test
from django.contrib import messages
from account.models import VideoProgress
from django.shortcuts import get_object_or_404
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from teachers.models import Video
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from django.contrib.auth.decorators import login_required
from django.views import View
from account.models import VideoProgress
from teachers.models import Video
from django.views.decorators.http import require_POST


def login(user):
    return user.is_authenticated

def is_teacher(user):
    return user.groups.filter(name='Teacher').exists()

def is_course_teacher(user, course):
    return user == course.teacher

def course(request):
    course_name = request.GET.get("q","")
    categories_data = Category.objects.all()
    courses = Course.objects.filter(title__contains = course_name)
    page = Paginator(courses, 9)  
    page_number = request.GET.get('page', 1)

    try:
        page_obj = page.page(page_number)
    except PageNotAnInteger:
        
        page_obj = page.page(1)
    except EmptyPage:
       
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

    page = Paginator(courses, 10) 
    page_number = request.GET.get('page', 1)

    try:
        page_obj = page.page(page_number)
    except PageNotAnInteger:
        page_obj = page.page(1)
    except EmptyPage:
        page_obj = page.page(page.num_pages)

    context = {
        "page_obj": page_obj,
        "categories_data": categories_data,  
    }
    return render(request, 'courses/course.html',context)


@user_passes_test(login)
def student_courses(request):
    categories_data = Category.objects.all()
    profile = request.user.profile
    courses = profile.enrolled_courses.all()

    page = Paginator(courses, 10)  
    page_number = request.GET.get('page', 1)

    try:
        page_obj = page.page(page_number)
    except PageNotAnInteger:
        page_obj = page.page(1)
    except EmptyPage:
        page_obj = page.page(page.num_pages)

    context = {
        "page_obj": page_obj,
        "categories_data": categories_data,  
    }
    return render(request, 'courses/study_courses.html',context)

def course_details(request, id):
    course = get_object_or_404(Course, slug=id)
    teacher = get_object_or_404(Profile, user__id=course.teacher.id, is_teacher=True)

    return render(request, 'courses/course_details.html', {
        "course": course,
        "alone": True,
        "teacher": teacher
    })

def course_details_id(request, id):
    course_data = Course.objects.all()

    course = [course for course in course_data if course.id == id]
    if len(course)>0:
        reverse_url = reverse("course_details", kwargs={"id": course[0].slug})
    
        return redirect(reverse_url)
    else:
        return HttpResponse("Course not found", status=404)

def categorie(request, id):

    course_name = request.GET.get("q","")

    categories_data = Category.objects.all()

    category = Category.objects.filter(slug=id).first()

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

@user_passes_test(login)
def enroll_course(request, id):
    course = get_object_or_404(Course, pk=id)
    profile = request.user.profile

    if course.teacher == request.user:
        messages.error(request, "You cannot enroll in your own course.")
        return redirect("course_details", id=course.id)

    if Enrollment.objects.filter(student=profile, course=course).exists():
        return redirect("course_detail", id=course.id)

    # Create enrollment record
    Enrollment.objects.create(student=profile, course=course)

    # Optionally update ManyToMany relationship (suitable for your case)
    profile.enrolled_courses.add(course)

    messages.success(request, "You have successfully enrolled in the course.")
    return redirect("course_details", id=course.id)

def course_detail(request, id):
    if not request.user.is_authenticated:
        return redirect("user_login")

    course = get_object_or_404(Course, pk=id)

    if course in request.user.profile.enrolled_courses.all() or course.teacher == request.user:
        profile = request.user.profile
        watched_videos = VideoProgress.objects.filter(student=profile, watched=True).values_list('video_id', flat=True)
        # Varsayılan ilk videoyu al
        first_video = None
        if course.sections.exists():
            first_section = course.sections.first()
            if first_section.videos.exists():
                first_video = first_section.videos.first()

        existing_note = ''
        if first_video:
            vp = VideoProgress.objects.filter(student=profile, video=first_video).first()
            if vp:
                existing_note = vp.note

        context = {
            'course': course,
            'watched_videos': set(watched_videos),
            'existing_note': existing_note,
            'video': first_video,
        }
        return render(request, 'teachers/course_detail.html', context)
    else:
        messages.error(request, "You are not enrolled in this course.")
        return redirect("course_details_id", id=id)

from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from django.views import View
from django.http import JsonResponse
from django.utils import timezone
import json

@method_decorator(csrf_exempt, name='dispatch')
class SaveNoteView(View):
    def post(self, request, video_id):
        if not request.user.is_authenticated:
            return JsonResponse({'status': 'error', 'message': 'You must be logged in.'}, status=401)

        try:
            video = Video.objects.get(pk=video_id)
        except Video.DoesNotExist:
            return JsonResponse({'status': 'error', 'message': 'Video not found.'}, status=404)

        profile = request.user.profile
        data = json.loads(request.body)
        note = data.get('note', '').strip()

        progress, _ = VideoProgress.objects.get_or_create(student=profile, video=video)
        progress.note = note
        progress.save()

        return JsonResponse({'status': 'ok'})


class VideoWatchedView(View):
    def post(self, request, video_id):
        if not request.user.is_authenticated:
            return JsonResponse({'error': 'You must be logged in.'}, status=401)

        try:
            video = Video.objects.get(pk=video_id)
        except Video.DoesNotExist:
            return JsonResponse({'error': 'Video not found.'}, status=404)

        profile = request.user.profile

        # Parse JSON data from request body
        try:
            data = json.loads(request.body)
        except json.JSONDecodeError:
            data = {}

        note = data.get('note', '')

        progress, created = VideoProgress.objects.get_or_create(
            student=profile,
            video=video,
            defaults={
                'watched': True,
                'watched_at': timezone.now(),
                'note': note
            }
        )

        if not created:
            progress.watched = True
            progress.watched_at = timezone.now()
            if note:
                progress.note = note
            progress.save()

        return JsonResponse({'status': 'ok'})
