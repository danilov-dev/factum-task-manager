from django.core.exceptions import ValidationError
from django import forms

from apps.ideas.models import Idea


class IdeaCreateForm(forms.ModelForm):
    class Meta:
        model = Idea
        fields = (
            'title',
            'about',
            'description',
            'category',
            'status',
            'is_published',
        )
        widgets = {
            'title': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': "idea's title",
            }),
            'about': forms.Textarea(attrs={
                'class': 'form-control',
                'placeholder': "about (< 250)",
            }),
            'description': forms.Textarea(attrs={
                'class': 'form-control markdown-textarea',
                'placeholder': 'Опишите вашу идею...',
                'rows': 200,
                'cols': 80,
                'style': 'width: 100%; min-height: 500px;',
            }),
            'category': forms.Select(attrs={'class': 'form-control'}),
            'status': forms.Select(attrs={'class': 'form-control'}),
            'is_published': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }

    def clean_status(self):
        status = self.cleaned_data['status']
        idea = self.instance

        if status in (Idea.Status.TEAM_ASSEMBLED, Idea.Status.IN_PROGRESS):
            if not idea.roles.exists():
                raise ValidationError('Нельзя собрать команду: роли не добавлены')

            if not idea.all_roles_filled:
                raise ValidationError('Нельзя собрать команду: не все роли заполнены')

        return status
