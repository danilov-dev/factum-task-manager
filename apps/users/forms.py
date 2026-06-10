from django import forms
from django.contrib.auth.forms import UserCreationForm, UserChangeForm, AuthenticationForm

from apps.users.models import User



class CustomUserChangeForm(UserChangeForm):
    """Форма изменения пользователя"""

    class Meta(UserCreationForm):
        model = User
        fields = ('username', 'email', 'first_name', 'last_name', 'bio', 'is_active', 'is_staff')
        widgets = {
            'username': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'User name'}),
            'email': forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'Email'}),
            'first_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'First name'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Last name'}),
            'bio': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Biography'}),
        }


class UserProfileForm(forms.ModelForm):
    """Форма для редактирования профиля"""

    class Meta:
        model = User
        fields = ('username', 'email', 'first_name', 'last_name', 'bio', 'avatar')
        widgets = {
            'username': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'User name'}),
            'first_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'First name'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Last name'}),
            'bio': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Biography'}),
            'avatar': forms.FileInput(attrs={'class': 'form-control'}),
        }
