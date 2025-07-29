from django.db import models
from django.utils.text import slugify
# Create your models here.

class Category(models.Model):
    name = models.CharField(max_length=100)
    tag = models.CharField(max_length=100, unique=True,blank=True)  

    def save(self, *args, **kwargs):
        if not self.tag:  
            self.tag = self.name.replace(" ", "_")

        self.name = self.name.capitalize()
        self.tag = self.tag.lower()

        super().save(*args, **kwargs)

    def __str__(self):
        return self.name
    

from django.db import models

class Course(models.Model):
    title = models.CharField(max_length=100)
    description = models.TextField()
    category = models.ManyToManyField(Category, related_name='courses')
    img = models.ImageField(upload_to='images/')
    date = models.DateField(auto_now=True)
    tag = models.SlugField(max_length=100, unique=True, blank=True)
    is_active = models.BooleanField(default=True)

    def save(self, *args, **kwargs):
        if not self.tag:  
            self.tag = slugify(self.title)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.title



