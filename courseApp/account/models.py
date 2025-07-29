from django.db import models
from django.contrib.auth.models import User
from courses.models import Course

# Create your models here.


class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    is_teacher = models.BooleanField(default=False)
    enrolled_courses = models.ManyToManyField(Course, related_name='enrolled_students', blank=True)


    def __str__(self):
        return self.user.get_full_name()

    @property
    def full_name(self):
        return self.user.get_full_name()
    
