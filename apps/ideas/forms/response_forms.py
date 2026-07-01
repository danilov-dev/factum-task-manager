from django import forms

from apps.ideas.models import IdeaResponse


class ResponseCreateForm(forms.Form):
    """Класс формы создания отклика на роль в идее"""
    message = forms.CharField(
        widget=forms.Textarea(attrs={
            'rows': 4,
            'placeholder': 'Расскажите о себе и почему вы подходите на эту роль...',
            'class': 'form-control'
        }),
        required=False,
        label='Сообщение'
    )
