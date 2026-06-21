from django import forms

from apps.ideas.models import Idea


class IdeaCreateForm(forms.ModelForm):
    class Meta:
        model = Idea
        fields = (
            'title',
            'description',
            'category',
            'status',
            'is_published'
        )
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control', 'placeholder': "idea's title"}),
            'description': forms.Textarea(attrs={'class': 'form-control description', 'placeholder': "description"}),
            'category': forms.Select(attrs={'class': 'form-control'}),
            'status': forms.Select(attrs={'class': 'form-control'}),
            'is_published': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }