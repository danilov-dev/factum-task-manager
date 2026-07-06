from django import forms

from apps.posts.models import Post


class PostCreateForm(forms.ModelForm):
    """Форма создания поста"""

    class Meta:
        model = Post
        fields = ['title', 'content']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control'}),
            'content': forms.Textarea(attrs={
                'class': 'form-control markdown-textarea',
                'rows': 200,
                'cols': 80,
                'style': 'width: 100%; min-height: 500px;',
            }),
        }
