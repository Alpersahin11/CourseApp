from ..models import Course
from django.forms import ModelForm, TextInput, Textarea, ClearableFileInput, SelectMultiple
from PIL import Image

class course_control(ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.warning = None  # özel uyarı

    class Meta:
        model = Course
        fields = ["title", "description", "img", "category"]
        widgets = {
            "title": TextInput(attrs={"class": "form-control"}),
            "description": Textarea(attrs={"class": "form-control", "rows": 4}),
            "img": ClearableFileInput(attrs={"class": "form-control"}),
            "category": SelectMultiple(attrs={"class": "form-select", "size": "5"}),
        }

    def clean_img(self):
        image = self.cleaned_data.get("img")

        if image:
            img = Image.open(image)
            width, height = img.size
            ratio = width / height

            # 16:9 oranı yaklaşık 1.777...
            if not (1.76 <= ratio <= 1.79):
                self.warning = "The image you uploaded doesn't match the recommended 16:9 aspect ratio. For best results, use sizes like 1920x1080 or 1280x720."

        return image
