from django.urls import path,include
from . import views


urlpatterns = [
    path('', views.course,name="course"),
    path('home/', views.home, name='home'),
    path('my_course/', views.my_course, name='my_courses'),
    path('create_course/', views.create_course, name='create_course'),
    path('edit_course/<int:id>', views.edit_course, name='edit_course'),
    path('delete_course/<int:id>', views.delete_course, name='delete_course'),
    path('source/', views.source_course, name='source'),
    path('contact/', views.contact, name='contact'),
    path('course/<int:id>', views.course_details_id, name='course_details_id'),
    path('course/<str:id>', views.course_details, name='course_details'),
    path('course/category/<id>', views.categorie, name='course_categorie'),
]