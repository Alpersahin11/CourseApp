from ..models import Course

from django.forms import ModelForm, TextInput, Textarea, ClearableFileInput, SelectMultiple

class course_control(ModelForm):
    class Meta:
        model = Course
        fields = ["title", "description", "img", "category"]
        widgets = {
            "title": TextInput(attrs={"class": "form-control"}),
            "description": Textarea(attrs={"class": "form-control", "rows": 4}),
            "img": ClearableFileInput(attrs={"class": "form-control"}),
            "category": SelectMultiple(attrs={"class": "form-select", "size": "5"}),
        }
