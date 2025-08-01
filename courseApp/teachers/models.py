import os
from django.utils.text import slugify
from django.db import models
from courses.models import Course

def video_upload_path(instance, filename):
    course_tag = instance.section.course.tag
    section_slug = slugify(instance.section.title)
    base, ext = os.path.splitext(filename)
    return f"videos/{course_tag}/{section_slug}/{base}{ext}"

class Section(models.Model):
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='sections')
    title = models.CharField(max_length=255)
    order = models.PositiveIntegerField(default=0)
    def __str__(self):
        return f"{self.course.title} - {self.title}"

class Video(models.Model):
    section = models.ForeignKey(Section, on_delete=models.CASCADE, related_name="videos")
    title = models.CharField(max_length=200)
    video_file = models.FileField(upload_to=video_upload_path)
    order = models.PositiveIntegerField(default=0)

    def __str__(self):
        return f"{self.section.title} - {self.title}"
