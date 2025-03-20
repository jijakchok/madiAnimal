from django import forms
from .models import Animal

class AnimalForm(forms.ModelForm):
    class Meta:
        model = Animal
        fields = ['comment', 'number', 'location']

    def clean_number(self):
        number = self.cleaned_data['number']
        if not number.isdigit() or len(number) != 11:
            raise forms.ValidationError("Номер должен состоять из 11 цифр.")
        return int(number)  # Преобразуйте строку в число

    def clean_location(self):
        location = self.cleaned_data['location']
        if len(location) < 3 or len(location) > 100:
            raise forms.ValidationError("Местоположение должно быть от 3 до 100 символов.")
        return location