from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User

from .models import Exercise, WorkoutDay


class WorkoutDayForm(forms.ModelForm):
    class Meta:
        model = WorkoutDay
        fields = ['name']
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'input',
                'placeholder': 'مثلاً: روز ۵ یا سینه و سه‌سر',
            })
        }
        labels = {'name': 'نام روز'}


class ExerciseForm(forms.ModelForm):
    class Meta:
        model = Exercise
        fields = ['name', 'exercise_type']
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'input',
                'placeholder': 'مثلاً: پرس سینه هالتر',
            }),
            'exercise_type': forms.Select(attrs={'class': 'input'}),
        }
        labels = {'name': 'نام حرکت جدید', 'exercise_type': 'نوع حرکت'}


class SignUpForm(UserCreationForm):
    class Meta:
        model = User
        fields = ['username', 'password1', 'password2']