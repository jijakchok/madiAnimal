from django import forms
from .models import Animal

class AnimalForm(forms.ModelForm):
    class Meta:
        model = Animal
        fields = ['comment', 'number', 'location']  # Уберите поле 'image'