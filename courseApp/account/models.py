from django.db import models
from django.contrib.auth.models import User
from courses.models import Course
from django_ckeditor_5.fields import CKEditor5Field
from PIL import Image
from django.core.files.base import ContentFile
from io import BytesIO
from django.db import models
from django.utils import timezone
from teachers.models import Video
# Create your models here.


class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    is_teacher = models.BooleanField(default=False)
    enrolled_courses = models.ManyToManyField(Course, related_name='enrolled_students', blank=True)
    image = models.ImageField(upload_to='profile_images/', blank=True, null=True)
    bio = CKEditor5Field(blank=True, null=True)


    def __str__(self):
        return self.user.get_full_name()

    @property
    def full_name(self):
        return self.user.get_full_name()
    
    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)

        if self.image:
            try:
                img = Image.open(self.image.path)

                max_size = (256, 256)

                if img.height > 256 or img.width > 256:
                    img.thumbnail(max_size)

                    # PNG/JPG formatına göre kaydet
                    img_format = img.format if img.format else 'JPEG'

                    # Yolu tekrar alıp üzerine yaz
                    img.save(self.image.path, img_format)

            except Exception as e:
                print("Görsel yeniden boyutlandırılırken hata:", e)


class Enrollment(models.Model):
    student = models.ForeignKey(Profile, on_delete=models.CASCADE)
    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    enrolled_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('student', 'course')  

    def __str__(self):
        # Burada Profile içindeki User'ın username'ine erişiyoruz
        return f"{self.student.user.username} - {self.course.title}"


class VideoProgress(models.Model):
    student = models.ForeignKey(Profile, on_delete=models.CASCADE)
    video = models.ForeignKey(Video, on_delete=models.CASCADE)
    watched = models.BooleanField(default=False)
    watched_at = models.DateTimeField(null=True, blank=True)
    note = models.TextField(blank=True)

    class Meta:
        unique_together = ('student', 'video')

    def __str__(self):
        return f"{self.student.user.username} - {self.video.section.course.title} - {self.video.title}"
