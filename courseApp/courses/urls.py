from django.urls import path,include
from . import views


urlpatterns = [
    path('', views.course,name="course"),
    path('study_course/', views.student_courses, name='student_courses'),
    path('enroll_course/<int:id>', views.enroll_course, name='enroll_course'),
    path('source/', views.source_course, name='source'),
    path('category/<id>', views.categorie, name='course_categorie'),
    path('<int:id>', views.course_details_id, name='course_details_id'),
    path('<str:id>', views.course_details, name='course_details'),
    path('lesson/<int:id>/', views.course_detail, name='course_detail'),

]