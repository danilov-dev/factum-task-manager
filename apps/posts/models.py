from django.db import models
from django.db.models import ForeignKey
from markdownx.models import MarkdownxField

from apps.ideas.models import Idea
from apps.users.models import User


class Post(models.Model):
    """Класс постов у идеи"""
    title = models.CharField(max_length=200)
    content = MarkdownxField(verbose_name='Контент')
    idea = models.ForeignKey(
        Idea,
        on_delete=models.CASCADE,
        related_name='roles',
        verbose_name='Идея',
    )
    author = ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='posts',
        verbose_name="Пост"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

