from django import forms
from django.forms import inlineformset_factory

from apps.ideas.models import IdeaRole, IdeaRoleSkill


class RoleSkillForm(forms.ModelForm):
    class Meta:
        model = IdeaRoleSkill
        fields = ('skill', 'is_required')
        widgets = {
            'skill': forms.HiddenInput(),
            'is_required': forms.CheckboxInput(attrs={'class': 'form-check-input skill-required'}),
        }


class RoleCreateForm(forms.ModelForm):
    class Meta:
        model = IdeaRole
        fields = (
            'title',
            'description',
            'count_needed',
            'is_open',
        )
        widgets = {
            'title': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Название роли',
            }),
            'description': forms.Textarea(attrs={
                'class': 'form-control',
                'placeholder': 'Описание роли',
            }),
            'count_needed': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': 1,
            }),
            'is_open': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }

    def __init__(self, *args, **kwargs):
        self.idea = kwargs.pop('idea', None)
        super().__init__(*args, **kwargs)

    def save(self, commit=True):
        role = super().save(commit=False)

        if self.idea:
            role.idea = self.idea

        if commit:
            role.save()

        return role


RoleSkillFormSet = inlineformset_factory(
    IdeaRole,
    IdeaRoleSkill,
    form=RoleSkillForm,
    extra=0,
    can_delete=True,
)
