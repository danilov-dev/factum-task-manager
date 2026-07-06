import logging
from django.core.exceptions import ValidationError
from django.db import models
from django.db.models import Exists
from markdownx.models import MarkdownxField
from config import settings

logger = logging.getLogger(__name__)


class IdeaQuerySet(models.QuerySet):
    """Кастомный QuerySet для работы с идеями."""

    def visible(self):
        """Идеи, видимые в публичной ленте."""
        return self.filter(
            is_published=True,
            status__in=[
                Idea.Status.OPEN,
                Idea.Status.TEAM_ASSEMBLED,
                Idea.Status.IN_PROGRESS,
            ]
        ).select_related('author').prefetch_related('roles')

    def by_category(self, category: str):
        """Идеи по категории."""
        return self.visible().filter(category=category)

    def for_user(self, user, viewer=None):
        """Идеи пользователя с учётом прав просмотра."""
        qs = self.filter(author=user)
        if viewer != user:
            qs = qs.visible()
        return qs.order_by('-created_at')

    def with_stats(self):
        """Идеи с оптимизированными связями для детального просмотра."""
        return self.select_related('author').prefetch_related(
            'roles',
            'roles__responses',
        )


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
        verbose_name='Автор',
    )
    title = models.CharField(max_length=255, verbose_name='Название')
    about = models.CharField(max_length=250, null=True, verbose_name='Суть идеи')
    description = MarkdownxField(verbose_name='Описание')
    category = models.CharField(
        max_length=50,
        choices=Category.choices,
        verbose_name='Категория',
    )
    status = models.CharField(
        max_length=50,
        choices=Status.choices,
        verbose_name='Статус',
    )
    is_published = models.BooleanField(
        default=False,
        verbose_name='Опубликована',
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Создана',
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name='Обновлена',
    )

    objects = IdeaQuerySet.as_manager()

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
        if not self.roles.exists():
            return False
        return not self.roles.filter(
            count_filled__lt=models.F('count_needed')
        ).exists()

    @property
    def unfilled_roles_count(self):
        return self.roles.filter(
            count_filled__lt=models.F('count_needed')
        ).count()


class IdeaRoleQuerySet(models.QuerySet):
    """Кастомный QuerySet для ролей."""

    def for_idea(self, idea_id: int):
        """Роли для конкретной идеи с оптимизацией."""
        return self.filter(idea_id=idea_id).select_related('idea').prefetch_related(
            'necessary_skills__skill',
        )

    def with_details(self):
        """Роли с детальной информацией о навыках."""
        return self.prefetch_related(
            'necessary_skills',
            'necessary_skills__skill',
        )


class IdeaRole(models.Model):
    """Роль участника команды."""

    idea = models.ForeignKey(
        Idea,
        on_delete=models.CASCADE,
        related_name='roles',
        verbose_name='Инициатива',
    )
    title = models.CharField(
        max_length=150,
        verbose_name='Название роли',
    )
    description = models.TextField(
        blank=True,
        verbose_name='Что нужно делать',
    )
    skills = models.ManyToManyField(
        'users.Skill',
        through='IdeaRoleSkill',
        related_name='roles_necessary_this',
        verbose_name='Необходимые навыки',
    )
    count_needed = models.PositiveIntegerField(
        default=1,
        verbose_name='Необходимое количество',
    )
    count_filled = models.PositiveIntegerField(
        default=0,
        verbose_name='Количество набранных',
    )
    is_open = models.BooleanField(
        default=True,
        verbose_name='Открыт для откликов',
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Создана',
    )

    objects = IdeaRoleQuerySet.as_manager()

    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Роль в инициативе'
        verbose_name_plural = 'Роли в инициативе'

    def __str__(self):
        return f'{self.idea} -> {self.title}'

    @property
    def spots_left(self):
        """Сколько свободных мест."""
        return max(0, self.count_needed - self.count_filled)

    @property
    def required_skills(self):
        return self.skills.filter(necessary_in_roles__is_required=True)

    def close_if_full(self):
        """Закрыть набор, если все места заняты."""
        if self.count_filled >= self.count_needed:
            self.is_open = False
            self.save(update_fields=['is_open'])


class IdeaRoleSkill(models.Model):
    """Сущность для связи роли и навыков."""

    role = models.ForeignKey(
        'IdeaRole',
        on_delete=models.CASCADE,
        related_name='necessary_skills',
        verbose_name='Роль',
    )
    skill = models.ForeignKey(
        'users.Skill',
        on_delete=models.CASCADE,
        related_name='necessary_in_roles',
        verbose_name='Навык',
    )
    is_required = models.BooleanField(
        default=True,
        verbose_name='Обязательный навык',
        help_text='Если False, навык будет считаться преимуществом, но не строгим требованием',
    )

    class Meta:
        verbose_name = 'Требование к навыку в роли'
        verbose_name_plural = 'Требования к навыкам в ролях'
        constraints = [
            models.UniqueConstraint(
                fields=['role', 'skill'],
                name='unique_role_skill_in_role',
            )
        ]

    def __str__(self):
        required_text = 'Обязательно' if self.is_required else 'Желательно'
        return f'{self.role.title} -> {self.skill.name} ({required_text})'


class IdeaResponseQuerySet(models.QuerySet):
    """Кастомный QuerySet для откликов."""

    def pending(self):
        """Отклики на рассмотрении."""
        return self.filter(status=IdeaResponse.Status.PENDING)

    def by_status(self, status):
        """Фильтр по статусу."""
        if isinstance(status, list):
            return self.filter(status__in=status)
        elif status != 'all':
            return self.filter(status=status)
        return self

    def for_user(self, user):
        """Отклики пользователя с оптимизацией."""
        return self.filter(user=user).select_related(
            'role',
            'role__idea',
            'role__idea__author'
        )

    def for_idea(self, idea):
        """Отклики на идею с оптимизацией."""
        return self.filter(role__idea=idea).select_related('user', 'role')


class IdeaResponse(models.Model):
    """Отклик пользователя на роль в инициативе."""

    class Status(models.TextChoices):
        PENDING = 'pending', 'на рассмотрении'
        APPROVED = 'approved', 'принят'
        REJECTED = 'rejected', 'отклонен'

    idea = models.ForeignKey(
        Idea,
        on_delete=models.CASCADE,
        related_name='responses',
        verbose_name='Инициатива',
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='responses',
        verbose_name='Кто откликнулся',
    )
    role = models.ForeignKey(
        IdeaRole,
        on_delete=models.CASCADE,
        related_name='responses',
        verbose_name='Роль',
    )
    message = models.TextField(
        blank=True,
        verbose_name='Сопроводительное письмо',
    )
    status = models.CharField(
        max_length=50,
        choices=Status.choices,
        default=Status.PENDING,
        verbose_name='Статус',
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Создан',
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name='Обновлен',
    )

    objects = IdeaResponseQuerySet.as_manager()

    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Отклик'
        verbose_name_plural = 'Отклики'
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'role'],
                name='unique_response_per_role',
            )
        ]

    def __str__(self):
        return f'{self.user} -> {self.role.title} ({self.get_status_display()})'

    def clean(self):
        super().clean()
        if not self.role.is_open:
            logger.warning('Попытка отклика на закрытую роль %s (id=%d) '
                           'пользователем %s',
                           self.role.title, self.role.pk, self.user, )
            raise ValidationError('Эта роль больше не активна')
        if self.role.spots_left <= 0:
            logger.warning(
                'Попытка отклика на заполненную роль %s (id=%d)',
                self.role.title, self.role.pk,
            )
            raise ValidationError('Все места на эту роль уже заняты')
        if self.user == self.idea.author:
            logger.warning(
                'Автор %s попытался откликнуться на свою инициативу %s',
                self.user, self.idea,
            )
            raise ValidationError('Автор идеи не может откликнуться на свою инициативу')
