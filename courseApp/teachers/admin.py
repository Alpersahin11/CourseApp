from django.contrib import admin
from .models import Section, TeacherRequest, Video

class VideoInline(admin.TabularInline):
    model = Video
    extra = 1

class SectionAdmin(admin.ModelAdmin):
    list_display = ('title', 'course', 'order')
    list_filter = ('course',)
    ordering = ('course', 'order')
    inlines = [VideoInline]

class CourseAdmin(admin.ModelAdmin):
    list_display = ('title', 'slug')
    prepopulated_fields = {'slug': ('title',)}

admin.site.register(TeacherRequest)
admin.site.register(Section, SectionAdmin)
