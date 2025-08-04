import os
from django.db import models
from django.utils.text import slugify
from courses.models import Course
from django.contrib.auth.models import User

def video_upload_path(instance, filename):
    course_slug = instance.section.course.slug
    section_slug = slugify(instance.section.title)
    base, ext = os.path.splitext(filename)
    return f"videos/{course_slug}/{section_slug}/{base}{ext}"


class Section(models.Model):
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='sections')
    title = models.CharField(max_length=255)
    order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ['order']

    def __str__(self):
        return f"{self.course.title} - {self.title}"


class Video(models.Model):
    section = models.ForeignKey(Section, on_delete=models.CASCADE, related_name="videos")
    title = models.CharField(max_length=200)
    video_file = models.FileField(upload_to=video_upload_path)
    order = models.PositiveIntegerField(default=0)
    duration = models.DurationField(null=True, blank=True)  # süre burada

    class Meta:
        ordering = ['order']

    def __str__(self):
        return f"{self.section.title} - {self.title}"

    def delete(self, *args, **kwargs):
        # Video dosyasını sil
        if self.video_file and os.path.isfile(self.video_file.path):
            os.remove(self.video_file.path)
        super().delete(*args, **kwargs)

class TeacherRequest(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
    ]

    teacher = models.ForeignKey(User, on_delete=models.CASCADE, related_name='teacher_requests')
    date_submitted = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='pending')
    note = models.TextField(blank=True, null=True)  # isteğe bağlı not

    def __str__(self):
        return f"{self.teacher.get_full_name()} - {self.status}"