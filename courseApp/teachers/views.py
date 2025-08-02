from django.shortcuts import get_object_or_404, redirect, render
from django.http import HttpResponse
from django.urls import reverse
from .models import Section, Video
from courses.models import Category, Course
from account.models import Profile
from django.core.paginator import Paginator ,EmptyPage, PageNotAnInteger
from .form.course_edit import course_control
from django.contrib.auth.decorators import user_passes_test
from django.contrib import messages
from django.shortcuts import render, redirect, get_object_or_404
from .models import Course, Section, Video
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST
from django.core.files.storage import FileSystemStorage

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

def is_teacher(user):
    return user.groups.filter(name='Teacher').exists()

@login_required
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


@login_required
def course_detail(request, id):
    course = get_object_or_404(Course, id=id)
    return render(request, "teachers/course_detail.html", {"course": course})


@login_required
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
            messages.error(request, "There was an error.")
            return render(request, "courses/create_course.html", {"form": form})
    else:
        form = course_control()
    return render(request, "courses/create_course.html", {"form": form})


@login_required
@user_passes_test(is_teacher)
def edit_course(request, id):
    course = get_object_or_404(Course, pk=id)
    if course.teacher != request.user:
        messages.error(request, "You do not have permission to edit this course.")
        return redirect("student_courses")

    if request.method == "POST":
        form = course_control(request.POST, request.FILES, instance=course)
        if form.is_valid():
            if form.warning:
                messages.warning(request, form.warning)
            form.save()
            messages.success(request, "Course updated successfully.")
            return redirect("teacher_courses")
        else:
            messages.error(request, "Error updating course.")
            return redirect("student_courses")
    else:
        form = course_control(instance=course)
    return render(request, "courses/create_course.html", {"form": form})


@login_required
@user_passes_test(is_teacher)
def delete_course(request, id):
    course = get_object_or_404(Course, pk=id)
    if course.teacher != request.user:
        messages.error(request, "You do not have permission to delete this course.")
        referer = request.META.get('HTTP_REFERER')
        if referer:
            return redirect(referer)
        else:
            return redirect("my_courses")

    if request.method == "POST":
        course.delete()
        messages.success(request, "Course deleted successfully.")
        return redirect("my_courses")

    return render(request, "courses/delete_course.html", {"course": course})


@login_required
@user_passes_test(is_teacher)
def teacher_courses(request):
    categories_data = Category.objects.all()
    courses = Course.objects.filter(teacher=request.user)

    paginator = Paginator(courses, 10)
    page_number = request.GET.get('page', 1)

    try:
        page_obj = paginator.page(page_number)
    except Exception:
        page_obj = paginator.page(1)

    context = {
        "page_obj": page_obj,
        "categories_data": categories_data,
    }
    return render(request, 'courses/admin_courses.html', context)


@login_required
def course_video_details(request, id):
    course = get_object_or_404(Course, id=id)
    return render(request, "courses/course_video_details.html", {"course": course})


@login_required
@user_passes_test(is_teacher)
def edit_course_structure(request, course_id):
    course = get_object_or_404(Course, id=course_id)
    if course.teacher != request.user:
        messages.error(request, "You do not have permission to edit this course.")
        return redirect('home')
    return render(request, 'teachers/edit_course_structure.html', {'course': course})


@login_required
@user_passes_test(is_teacher)
@require_POST
def add_section(request, course_id):
    course = get_object_or_404(Course, id=course_id)
    if course.teacher != request.user:
        messages.error(request, "You do not have permission to add sections.")
        return redirect('home')

    title = request.POST.get('title')
    order = course.sections.count()
    Section.objects.create(course=course, title=title, order=order)
    messages.success(request, "Section added successfully.")
    return redirect('edit_course_structure', course_id=course.id)


@login_required
@user_passes_test(is_teacher)
@require_POST
def add_video(request, section_id):
    section = get_object_or_404(Section, id=section_id)
    if section.course.teacher != request.user:
        messages.error(request, "You do not have permission to add videos.")
        return redirect('home')

    title = request.POST.get('title')
    video_file = request.FILES.get('video_file')
    order = section.videos.count()
    Video.objects.create(section=section, title=title, video_file=video_file, order=order)
    messages.success(request, "Video added successfully.")
    return redirect('edit_course_structure', course_id=section.course.id)


@login_required
@user_passes_test(is_teacher)
def move_section_up(request, section_id):
    section = get_object_or_404(Section, id=section_id)
    if section.course.teacher != request.user:
        messages.error(request, "You do not have permission to modify sections.")
        return redirect('home')

    previous = Section.objects.filter(course=section.course, order__lt=section.order).order_by('-order').first()
    if previous:
        section.order, previous.order = previous.order, section.order
        section.save()
        previous.save()
    return redirect('edit_course_structure', course_id=section.course.id)


@login_required
@user_passes_test(is_teacher)
def move_section_down(request, section_id):
    section = get_object_or_404(Section, id=section_id)
    if section.course.teacher != request.user:
        messages.error(request, "You do not have permission to modify sections.")
        return redirect('home')

    next_section = Section.objects.filter(course=section.course, order__gt=section.order).order_by('order').first()
    if next_section:
        section.order, next_section.order = next_section.order, section.order
        section.save()
        next_section.save()
    return redirect('edit_course_structure', course_id=section.course.id)


@login_required
@user_passes_test(is_teacher)
def move_video_up(request, video_id):
    video = get_object_or_404(Video, id=video_id)
    if video.section.course.teacher != request.user:
        messages.error(request, "You do not have permission to modify videos.")
        return redirect('home')

    previous = Video.objects.filter(section=video.section, order__lt=video.order).order_by('-order').first()
    if previous:
        video.order, previous.order = previous.order, video.order
        video.save()
        previous.save()
    return redirect('edit_course_structure', course_id=video.section.course.id)


@login_required
@user_passes_test(is_teacher)
def move_video_down(request, video_id):
    video = get_object_or_404(Video, id=video_id)
    if video.section.course.teacher != request.user:
        messages.error(request, "You do not have permission to modify videos.")
        return redirect('home')

    next_video = Video.objects.filter(section=video.section, order__gt=video.order).order_by('order').first()
    if next_video:
        video.order, next_video.order = next_video.order, video.order
        video.save()
        next_video.save()
    return redirect('edit_course_structure', course_id=video.section.course.id)


@login_required
@user_passes_test(is_teacher)
@require_POST
def delete_section(request, section_id):
    section = get_object_or_404(Section, id=section_id)
    if section.course.teacher != request.user:
        messages.error(request, "You do not have permission to delete this section.")
        return redirect('home')

    course_id = section.course.id
    section.delete()
    messages.success(request, "Section deleted successfully.")
    return redirect('edit_course_structure', course_id)


@login_required
@user_passes_test(is_teacher)
@require_POST
def delete_video(request, video_id):
    video = get_object_or_404(Video, id=video_id)
    if video.section.course.teacher != request.user:
        messages.error(request, "You do not have permission to delete this video.")
        return redirect('home')

    course_id = video.section.course.id
    video.delete()
    messages.success(request, "Video deleted successfully.")
    return redirect('edit_course_structure', course_id)


@login_required
@user_passes_test(is_teacher)
@require_POST
def edit_video(request, video_id):
    video = get_object_or_404(Video, id=video_id)
    if video.section.course.teacher != request.user:
        messages.error(request, "You do not have permission to edit this video.")
        return redirect('home')

    new_title = request.POST.get('title', '').strip()
    if new_title:
        video.title = new_title
        video.save()
        messages.success(request, "Video title updated.")
    return redirect('edit_course_structure', video.section.course.id)


@login_required
@user_passes_test(is_teacher)
@require_POST
def move_video_section(request, video_id):
    video = get_object_or_404(Video, id=video_id)
    if video.section.course.teacher != request.user:
        messages.error(request, "You do not have permission to move this video.")
        return redirect('home')

    new_section_id = request.POST.get('new_section')
    new_section = get_object_or_404(Section, id=new_section_id)

    if video.section != new_section:
        video.section = new_section
        video.order = new_section.videos.count()
        video.save()
        messages.success(request, "Video moved to another section.")
    return redirect('edit_course_structure', new_section.course.id)
