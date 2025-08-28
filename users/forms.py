from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import get_user_model

CustomUser = get_user_model()  # Получаем вашу пользовательскую модель


class CustomUserCreationForm(UserCreationForm):
    class Meta:
        model = CustomUser
        fields = ('email', 'password1', 'password2')

    def __init__(self, *args, **kwargs):  # Исправлено
        super().__init__(*args, **kwargs)  # Исправлено
        self.fields['email'].error_messages = {
            'unique': 'Пользователь с таким email уже существует.',
        }

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if CustomUser.objects.filter(email=email).exists():  # Проверка на уникальность
            raise forms.ValidationError(
                self.fields['email'].error_messages['unique']
            )
        return email
