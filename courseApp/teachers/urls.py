from django.contrib import admin
from django.urls import path,include
from django.conf.urls.static import static
from django.conf import settings
from . import views

urlpatterns = [
    path('', views.home,name="teacher"),
    path('teach_course/', views.teacher_courses, name='teacher_courses'),
    path('create_course/', views.create_course, name='create_course'),
    path('edit_course/<int:id>', views.edit_course, name='edit_course'),
    path('delete_course/<int:id>', views.delete_course, name='delete_course'),
    path('details/<int:id>',views.teacher_details,name='teacher_details'),


    path('course_video_details/<int:id>',views.course_video_details,name='course_video_details'),
    path('course/<int:course_id>/edit-structure/', views.edit_course_structure, name='edit_course_structure'),
    path('course/<int:course_id>/add-section/', views.add_section, name='add_section'),

    path('section/<int:section_id>/add-video/', views.add_video, name='add_video'),
    path('section/delete/<int:section_id>', views.delete_section, name='delete_section'),

    path('section/<int:section_id>/up/', views.move_section_up, name='move_section_up'),
    path('section/<int:section_id>/down/', views.move_section_down, name='move_section_down'),

    path('video/<int:video_id>/up/', views.move_video_up, name='move_video_up'),
    path('video/<int:video_id>/down/', views.move_video_down, name='move_video_down'),
    path('video/<int:video_id>', views.move_video_section, name='move_video_section'),

    path('video/edit/<int:video_id>', views.edit_video, name='edit_video'),

    path('video/delete/<int:video_id>', views.delete_video, name='delete_video'),

]