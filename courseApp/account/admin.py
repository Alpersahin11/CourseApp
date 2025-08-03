from django.contrib import admin
from .models import Profile,Enrollment,VideoProgress
# Register your models here.

admin.site.register(Profile)

@admin.register(Enrollment)
class EnrollmentAdmin(admin.ModelAdmin):
    list_display = ('student', 'course', 'enrolled_at')
    list_filter = ('enrolled_at',)

@admin.register(VideoProgress)
class VideoProgressAdmin(admin.ModelAdmin):
    list_display = ('student', 'video', 'watched', 'watched_at')
    list_filter = ('watched', 'watched_at')
