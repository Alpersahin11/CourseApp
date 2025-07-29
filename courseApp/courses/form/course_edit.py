from django.forms import ClearableFileInput, ModelForm, SelectMultiple, TextInput, Textarea
from ..models import Course

class course_control(ModelForm):
    class Meta:
        model = Course
        fields = ["title", "description", "img", "tag", "category"]
        widgets = {
            "title": TextInput(attrs={"class": "form-control"}),
            "description": Textarea(attrs={"class": "form-control"}),
            "img": ClearableFileInput(attrs={"class": "form-control"}),
            "tag": TextInput(attrs={"class": "form-control"}),
            "category": SelectMultiple(attrs={"class": "form-control"}),
        }
