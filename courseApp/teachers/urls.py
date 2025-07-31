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
    path('details/<int:id>',views.teacher_details,name='teacher_details')
]