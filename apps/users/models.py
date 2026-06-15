from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    """Кастомная модель пользователя"""
    bio = models.TextField(
        blank=True,
        verbose_name='О себе'
    )
    avatar = models.ImageField(
        upload_to='avatars/',
        blank=True,
        null=True,
        verbose_name='Аватар'
    )

    skills = models.ManyToManyField(
        'Skill',
        through='UserSkill',
        related_name='users',
        verbose_name='Навыки'
    )

    class Meta:
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'
        ordering = ['-date_joined']

    def __str__(self):
        return self.username or self.email


class Skill(models.Model):
    """Навык"""

    class Category(models.TextChoices):
        IT = 'it', 'IT и технологии'
        DESIGN = 'design', 'Дизайн'
        MARKETING = 'marketing', 'Маркетинг и SMM'
        MANAGEMENT = 'management', 'Управление проектами'
        FINANCE = 'finance', 'Финансы и фандрайзинг'
        WRITING = 'writing', 'Тексты и копирайтинг'
        EDUCATION = 'education', 'Образование и тренинги'
        OTHER = 'other', 'Другое'

    name = models.CharField(
        max_length=120,
        unique=True,
        verbose_name='Название'
    )
    category = models.CharField(
        max_length=30,
        choices=Category.choices,
        default=Category.OTHER,
        verbose_name='Категория'
    )

    class Meta:
        ordering = ['category', 'name']
        verbose_name = 'Навык'
        verbose_name_plural = 'Навыки'

    def __str__(self):
        return self.name

class UserSkill(models.Model):
    """Связь пользователя и навыков с уровнем владения"""

    class Level(models.TextChoices):
        BEGINNER = 'beginner', 'Начинающий'
        INTERMEDIATE = 'intermediate', 'Средний'
        ADVANCED = 'advanced', 'Продвинутый'
        EXPERT = 'expert', 'Эксперт'

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='user_skills',
    )
    skill = models.ForeignKey(
        Skill,
        on_delete=models.CASCADE,
        related_name='user_skills',
    )
    level = models.CharField(
        max_length=20,
        choices=Level.choices,
        default=Level.BEGINNER,
    )

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'skill'],
                name='unique_skill',
            )
        ]

    def __str__(self):
        return f'{self.user} - {self.skill.name} ({self.get_level_display()})'

