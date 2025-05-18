from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm

from django import forms
from .models import Application, Contest, UserProfile, Review
from .models import ApplicationField, ApplicationAnswer, Application


class LoginForm(AuthenticationForm):
    class Meta:
        model = User
        fields = ['username', 'password']
        widgets = {
            'username': forms.TextInput(attrs={'class': 'input-v'}),
            'password': forms.PasswordInput(attrs={'class': 'input-v'}),
        }


class ApplicationForm(forms.Form):
    def __init__(self, *args, **kwargs):
        contest = kwargs.pop('contest', None)
        user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)

        if contest:
            fields = contest.fields.order_by('order')
            for field in fields:
                field_name = f'field_{field.id}'
                initial = None

                # Загружаем старые ответы, если редактирование
                if user:
                    try:
                        app = Application.objects.get(user=user, contest=contest)
                        answer = app.answers.filter(field=field).first()
                        if answer:
                            initial = answer.value
                    except Application.DoesNotExist:
                        pass

                self.fields[field_name] = self.create_form_field(field, initial)

    def create_form_field(self, field, initial=None):
        field_kwargs = {
            'label': field.label,
            'required': field.required,
            'initial': initial
        }

        if field.field_type == 'text':
            return forms.CharField(**field_kwargs)
        elif field.field_type == 'email':
            return forms.EmailField(**field_kwargs)
        elif field.field_type == 'number':
            return forms.IntegerField(**field_kwargs)
        elif field.field_type == 'file':
            return forms.FileField(**field_kwargs)
        elif field.field_type == 'image':
            return forms.ImageField(**field_kwargs)
        elif field.field_type == 'choice':
            choices = [(choice.value, choice.value) for choice in field.choices.all()]
            return forms.ChoiceField(choices=choices, **field_kwargs)

        return forms.CharField(**field_kwargs)  # fallback

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

class ContestForm(forms.ModelForm):
    class Meta:
        model = Contest
        fields = ['title', 'description', 'regulations', 'start_date', 'end_date']

class ReviewForm(forms.ModelForm):
    class Meta:
        model = Review
        fields = ['innovation', 'feasibility', 'impact', 'presentation_quality', 'comment']
        widgets = {
            'innovation': forms.NumberInput(attrs={'min': 0, 'max': 20}),
            'feasibility': forms.NumberInput(attrs={'min': 0, 'max': 20}),
            'impact': forms.NumberInput(attrs={'min': 0, 'max': 20}),
            'presentation_quality': forms.NumberInput(attrs={'min': 0, 'max': 20}),
            'comment': forms.Textarea(attrs={'rows': 4}),
        }

    def save(self, commit=True):
        review = super().save(commit=False)
        review.total_score = (
            review.innovation + 
            review.feasibility + 
            review.impact + 
            review.presentation_quality
        )
        if commit:
            review.save()
        return review