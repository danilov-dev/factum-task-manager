from django.core.exceptions import ValidationError
from django.db import models

from config import settings
from ckeditor.fields import RichTextField


class Idea(models.Model):
    """
    Публичная инициатива.
    Основа для социальной работы. Видимая часть системы.
    """

    class Status(models.TextChoices):
        DRAFT = 'draft', 'черновик'
        OPEN = 'open', 'идет набор'
        TEAM_ASSEMBLED = 'team_assembled', 'команда собрана'
        IN_PROGRESS = 'in_progress', 'проект запущен'
        COMPLETED = 'completed', 'завершен'
        ARCHIVED = 'archived', 'в архиве'

    class Category(models.TextChoices):
        IT = 'it', 'IT'
        ECOLOGY = 'ecology', 'экология'
        ART = 'art', 'искусство'
        EDUCATION = 'education', 'образование'
        SPORT = 'sport', 'спорт'
        SOCIAL = 'social', 'социальная помощь'
        BUSINESS = 'business', 'бизнес и стартапы'
        OTHER = 'other', 'другое'

    author = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='ideas',
        verbose_name='Автор'
    )
    title = models.CharField(max_length=255, verbose_name='Название')
    description = RichTextField(verbose_name='Описание')
    category = models.CharField(
        max_length=50,
        choices=Category.choices,
        verbose_name='Категория'
    )
    status = models.CharField(
        max_length=50,
        choices=Status.choices,
        verbose_name='Статус'
    )
    is_published = models.BooleanField(
        default=False,
        verbose_name='Опубликована'
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Создана'
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name='Обновлена'
    )

    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Инициатива'
        verbose_name_plural = 'Инициативы'
        indexes = [
            models.Index(fields=['status', 'is_published']),
            models.Index(fields=['category']),
        ]

    def __str__(self):
        return self.title

    @property
    def is_visible(self):
        return self.is_published and self.status in (
            self.Status.OPEN,
            self.Status.TEAM_ASSEMBLED,
            self.Status.IN_PROGRESS,
        )

    @property
    def all_roles_filled(self):
        return self.roles.filter(
            count_filled__lt=models.F('count_needed')
        ).exists()


class IdeaRole(models.Model):
    """Роль участника команды"""
    idea = models.ForeignKey(
        Idea,
        on_delete=models.CASCADE,
        related_name='roles',
        verbose_name='Инициатива'
    )
    title = models.CharField(
        max_length=150,
        verbose_name='Название роли'
    )
    description = models.TextField(
        blank=True,
        verbose_name='Что нужно делать'
    )
    # skill = models.ForeignKey(
    #     'users.Skill',
    #     on_delete=models.SET_NULL,
    #     null=True,
    #     blank=True,
    #     related_name='roles',
    #     verbose_name='требуемый навык'
    # )

    skills = models.ManyToManyField(
        'users.Skill',
        through='IdeaRoleSkill',
        related_name='relose_necessary_this',
        verbose_name='Необходимые навыки'
    )
    count_needed = models.PositiveIntegerField(
        default=1,
        verbose_name='Необходимое количество'
    )
    count_filled = models.PositiveIntegerField(
        default=0,
        verbose_name='Количество набранных'
    )
    is_open = models.BooleanField(
        default=True,
        verbose_name='Открыт для откликов'
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Создана'
    )

    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Роль в инициативе'
        verbose_name_plural = 'Роли в инициативе'

    def __str__(self):
        return f'{self.idea} -> {self.title}'

    @property
    def spots_left(self):
        """Сколько свободных мест"""
        return max(0, self.count_needed - self.count_filled)

    @property
    def required_skills(self):
        return self.skills.filter(role_skill__is_required=True)

    def close_if_full(self):
        """Закрыть набор, если все места заняты"""
        if self.count_filled >= self.count_needed:
            self.is_open = False
            self.save(update_fields=['is_open'])


class IdeaRoleSkill(models.Model):
    """Сущность для связи роли и навыков """
    role = models.ForeignKey(
        'IdeaRole',
        on_delete=models.CASCADE,
        related_name='necessary_skills',
        verbose_name='Роль'
    )
    skill = models.ForeignKey(
        'users.Skill',
        on_delete=models.CASCADE,
        related_name='necessary_in_roles',
        verbose_name='Навык'
    )
    is_required = models.BooleanField(
        default=True,
        verbose_name='Обязательный навык',
        help_text='Если False, навык будет считаться преимуществом, но не строгим требованием'
    )

    class Meta:
        verbose_name = 'Требование к навыку в роли'
        verbose_name_plural = 'Требования к навыкам в ролях'
        constraints = [
            models.UniqueConstraint(
                fields=['role', 'skill'],
                name='unique_role_skill_in_role'
            )
        ]

    def __str__(self):
        required_text = 'Обязательно' if self.is_required else 'Желательно'
        return f'{self.role.title} -> {self.skill.name} ({required_text})'


class IdeaResponse(models.Model):
    """Отклик пользователя на роль в инициативе"""

    class Status(models.TextChoices):
        PENDING = 'pending', 'на рассмотрении'
        APPROVED = 'approved', 'принят'
        REJECTED = 'rejected', 'отклонен'

    idea = models.ForeignKey(
        Idea,
        on_delete=models.CASCADE,
        related_name='responses',
        verbose_name='Инициатива'
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='responses',
        verbose_name='Кто откликнулся'
    )
    role = models.ForeignKey(
        IdeaRole,
        on_delete=models.CASCADE,
        related_name='responses',
        verbose_name='Роль'
    )
    message = models.TextField(
        blank=True,
        verbose_name='Сопроводительное письмо'
    )
    status = models.CharField(
        max_length=50,
        choices=Status.choices,
        default=Status.PENDING,
        verbose_name='Статус'
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Создан'
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name='Обновлен'
    )

    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Отклик'
        verbose_name_plural = 'Отклики'
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'role'],
                name='unique_response_per_role'
            )
        ]

    def __str__(self):
        return f'{self.user} -> {self.role.title} ({self.get_status_display()})'

    def clean(self):
        super().clean()
        if not self.role.is_open:
            raise ValidationError('Эта роль больше не активна')
        if self.role.spots_left <= 0:
            raise ValidationError('Все места на эту роль уже заняты')
        if self.user == self.idea.author:
            raise ValidationError('Автор идеи не может откликнуться на свою инициативу')
