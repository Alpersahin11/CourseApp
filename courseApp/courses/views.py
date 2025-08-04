import json
from django.shortcuts import get_object_or_404, redirect, render
from django.http import HttpResponse
from django.urls import reverse

from courses.forms import CategoryForm
from .models import Category, Course
from account.models import Enrollment, Profile 
from django.core.paginator import Paginator ,EmptyPage, PageNotAnInteger
from django.contrib.auth.decorators import user_passes_test
from django.contrib import messages
from account.models import VideoProgress
from django.shortcuts import get_object_or_404
from django.http import JsonResponse
from django.utils import timezone
from teachers.models import Video
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from django.views import View
from account.models import VideoProgress
from teachers.models import Video
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from django.views import View
from django.http import JsonResponse
from django.utils import timezone
import json

def login(user):
    return user.is_authenticated

def is_teacher(user):
    return user.groups.filter(name='Teacher').exists()

def is_course_teacher(user, course):
    return user == course.teacher

def course(request):
    course_name = request.GET.get("q","")
    categories_data = Category.objects.all()
    courses = Course.objects.filter(title__contains = course_name,is_active = True)
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
    courses = Course.objects.filter(title__contains = course_name,is_active = True)

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
        page_obj = page.page(1)
    except EmptyPage:
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

    Enrollment.objects.create(student=profile, course=course)

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

        selected_video_id = request.GET.get('video_id')

        selected_video = None
        if selected_video_id:
            selected_video = Video.objects.filter(id=selected_video_id, section__course=course).first()

        if not selected_video and course.sections.exists():
            first_section = course.sections.first()
            if first_section.videos.exists():
                selected_video = first_section.videos.first()

        existing_note = ''
        if selected_video:
            vp = VideoProgress.objects.filter(student=profile, video=selected_video).first()
            if vp:
                existing_note = vp.note

        if selected_video and selected_video.duration:
            total_seconds = int(selected_video.duration.total_seconds())
            minutes = total_seconds // 60
            seconds = total_seconds % 60
            formatted_duration = f"{minutes}:{seconds:02d}"
        else:
            formatted_duration = None

        video_durations = {}
        for section in course.sections.all():
            for video in section.videos.all():
                if video.duration:
                    total_seconds = int(video.duration.total_seconds())
                    minutes = total_seconds // 60
                    seconds = total_seconds % 60
                    video_durations[video.id] = f"{minutes}:{seconds:02d}"


        context = {
            'course': course,
            'watched_videos': set(watched_videos),
            'existing_note': existing_note,
            'video': selected_video,
            'video_durations': video_durations,
            'formatted_duration': formatted_duration,
            'selected_video_id': int(selected_video_id) if selected_video_id else (selected_video.id if selected_video else None),
        }
        return render(request, 'teachers/course_detail.html', context)
    else:
        messages.error(request, "You are not enrolled in this course.")
        return redirect("course_details_id", id=id)



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
    
    
@user_passes_test(lambda u: u.is_superuser)
def manage_categories(request, edit_id=None):
    categories = Category.objects.all()
    form = CategoryForm()
    edit_form = None
    category_to_edit = None

    # Kategori ekleme
    if request.method == 'POST' and not edit_id:
        form = CategoryForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('manage_categories')

    # Kategori düzenleme
    if edit_id:
        category_to_edit = get_object_or_404(Category, id=edit_id)
        if request.method == 'POST':
            edit_form = CategoryForm(request.POST, instance=category_to_edit)
            if edit_form.is_valid():
                edit_form.save()
                return redirect('manage_categories')
        else:
            edit_form = CategoryForm(instance=category_to_edit)

    return render(request, 'courses/manage_categories.html', {
        'categories': categories,
        'form': form,
        'edit_form': edit_form,
        'edit_id': edit_id,
    })

@user_passes_test(lambda u: u.is_superuser)
def delete_category(request, id):
    category = get_object_or_404(Category, id=id)
    category.delete()
    return redirect('manage_categories')