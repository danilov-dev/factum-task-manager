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
        IT_DEV = 'it_dev', 'IT и Разработка'
        DESIGN = 'design', 'Дизайн и Графика'
        MARKETING = 'marketing', 'Маркетинг, PR и SMM'
        CONTENT = 'content', 'Тексты, Копирайтинг и Переводы'
        MEDIA = 'media', 'Видео, Аудио и Фотография'
        MANAGEMENT = 'management', 'Управление проектами (PM)'
        EVENTS = 'events', 'Организация мероприятий'
        FINANCE = 'finance', 'Финансы и Фандрайзинг'
        LEGAL = 'legal', 'Юридическая помощь'
        EDUCATION = 'education', 'Образование, Менторство и Психология'
        RESEARCH = 'research', 'Наука и Аналитика'
        ART = 'art', 'Искусство и Культура'
        VOLUNTEERING = 'volunteering', 'Волонтёрство и логистика'
        HEALTH = 'health', 'Здоровье и Медицина'
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

