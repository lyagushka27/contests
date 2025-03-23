from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm

from django import forms
from .models import Application, UserProfile


class LoginForm(AuthenticationForm):
    class Meta:
        model = User
        fields = ['username', 'password']
        widgets = {
            'username': forms.TextInput(attrs={'class': 'input-v'}),
            'password': forms.PasswordInput(attrs={'class': 'input-v'}),
        }


class ApplicationForm(forms.ModelForm):
    NOMINATION_CHOICES = [
        ('informatics', 'Информатика'),
        ('mathematics', 'Математика'),
        ('history', 'История'),
        ('economics', 'Экономика'),
        # Добавьте другие номинации по необходимости
    ]

    nomination = forms.ChoiceField(choices=NOMINATION_CHOICES, label='Номинация', widget=forms.Select(attrs={'class': 'input-v'}))

    class Meta:
        model = Application
        fields = [
            'first_name', 'last_name', 'middle_name', 'phone', 'email',
            'organization', 'age', 'class_number', 'nomination',
            'startup_name', 'startup_description', 'presentation', 'cover'
        ]
        labels = {
            'first_name': 'Имя',
            'last_name': 'Фамилия',
            'middle_name': 'Отчество',
            'phone': 'Номер телефона',
            'email': 'Email',
            'organization': 'Название образовательной организации',
            'age': 'Возраст',
            'class_number': 'Номер класса',
            'startup_name': 'Название стартапа',
            'startup_description': 'Описание стартапа',
            'presentation': 'Презентация (PDF)',
            'cover': 'Обложка (JPG)',
        }
        widgets = {
            'first_name': forms.TextInput(attrs={'class': 'input-v', 'placeholder': 'Софья'}),
            'last_name': forms.TextInput(attrs={'class': 'input-v', 'placeholder': 'Гиенко'}),
            'middle_name': forms.TextInput(attrs={'class': 'input-v', 'placeholder': 'Константинова'}),
            'phone': forms.TextInput(attrs={'class': 'input-v', 'placeholder': '+7 999 999 99 99'}),
            'email': forms.EmailInput(attrs={'class': 'input-v', 'placeholder': 'turkish.sweetshop@gmail.com'}),
            'organization': forms.TextInput(attrs={'class': 'input-v', 'placeholder': 'АлГПУ'}),
            'age': forms.TextInput(attrs={'class': 'input-v', 'placeholder': '17'}),
            'class_number': forms.TextInput(attrs={'class': 'input-v', 'placeholder': '11'}),
            'startup_name': forms.TextInput(attrs={'class': 'input-v', 'placeholder': 'TechWave'}),
            'startup_description': forms.Textarea(attrs={'class': 'input-v', 'rows': 4, 'placeholder': 'TechWave - это инновационный стартап...'}),
            'presentation': forms.FileInput(attrs={'class': 'file-upload'}),
            'cover': forms.FileInput(attrs={'class': 'file-upload'}),
        }

        def __init__(self, *args, **kwargs):
            super().__init__(*args, **kwargs)
            if 'initial' not in kwargs:
                kwargs['initial'] = {}
            kwargs['initial'].update({
                'first_name': self.instance.user.userprofile.first_name, # type: ignore
                'last_name': self.instance.user.userprofile.last_name, # type: ignore
                'middle_name': self.instance.user.userprofile.middle_name, # type: ignore
            })

class RegisterForm(UserCreationForm):
    first_name = forms.CharField(max_length=100, required=True)
    last_name = forms.CharField(max_length=100, required=True)
    middle_name = forms.CharField(max_length=100, required=True)
    email = forms.EmailField(required=True)

    class Meta:
        model = User
        fields = ('username', 'first_name', 'last_name', 'middle_name' , 'email', 'password1', 'password2')

    def save(self, commit=True):
        user = super().save(commit=commit)
        UserProfile.objects.create(
            user=user,
            first_name=self.cleaned_data['first_name'],
            last_name=self.cleaned_data['last_name'],
            middle_name=self.cleaned_data['middle_name']
        )
        return user
