import os
from django.db import models
from django.utils.text import slugify
from PIL import Image
from django.conf import settings
from django.contrib.auth.models import User
from ckeditor.fields import RichTextField

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
    description = RichTextField(blank=True, null=True)
    category = models.ManyToManyField(Category, related_name='courses')
    img = models.ImageField(upload_to='images/')
    date = models.DateField(auto_now=True)
    tag = models.SlugField(max_length=100, unique=True, blank=True)
    is_active = models.BooleanField(default=True)
    teacher = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)

    def save(self, *args, **kwargs):
        if not self.tag:
            self.tag = slugify(self.title)

        super().save(*args, **kwargs)

        # Görseli yeniden boyutlandır (yalnızca yeni görsel varsa)
        if self.img:
            img_path = os.path.join(settings.MEDIA_ROOT, self.img.name)
            try:
                img = Image.open(img_path)
                img = img.convert("RGB")
                img = img.resize((800, 450))  # Yeni boyut (16:9 oran)
                img.save(img_path)
            except Exception as e:
                print("Görsel işleme hatası:", e)


    def __str__(self):
        return self.title
    


