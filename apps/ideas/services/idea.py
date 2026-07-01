from django.shortcuts import get_object_or_404

from apps.ideas.models import Idea


def create_idea(*, author, title,about, description, category):
    """Создать черновик идеи."""
    idea = Idea.objects.create(
        author=author,
        title=title,
        about=about,
        description=description,
        category=category,
        status=Idea.Status.DRAFT,
        is_published=False,
    )
    return idea


def update_idea(*, idea_id, title, about, description, category, status):
    """Обновить существующую идею."""
    idea = get_object_or_404(Idea, pk=idea_id)
    idea.title = title
    idea.about = about
    idea.description = description
    idea.category = category
    idea.status = status
    idea.save()
    return idea


def get_idea(*, idea_id: int):
    """Получить идею по ID."""
    return get_object_or_404(
        Idea.objects.prefetch_related('roles'),
        pk=idea_id,
    )


def get_idea_with_stats(*, idea_id: int):
    """Получить идею со статистикой по ролям."""
    idea = get_object_or_404(
        Idea.objects.select_related('author').prefetch_related('roles'),
        pk=idea_id,
    )
    idea.open_roles_count = idea.roles.filter(is_open=True).count()
    idea.has_team = any(
        role.count_filled > 0
        for role in idea.roles.all()
    )
    idea.search_pronoun = 'Мы ищем' if idea.has_team else 'Я ищу'

    return idea


def get_visible_ideas():
    """Возвращает идеи, видимые в публичной ленте."""
    return Idea.objects.filter(
        is_published=True,
        status__in=(
            Idea.Status.OPEN,
            Idea.Status.TEAM_ASSEMBLED,
            Idea.Status.IN_PROGRESS,
        ),
    ).select_related('author').prefetch_related('roles')


def get_ideas_by_category(category: str):
    """Возвращает идеи по категории."""
    return get_visible_ideas().filter(category=category)


def get_user_ideas(user, viewer=None):
    """Идеи пользователя с учётом прав просмотра."""
    qs = user.ideas.all()
    if viewer != user:
        qs = qs.filter(
            is_published=True,
            status__in=(
                Idea.Status.OPEN,
                Idea.Status.TEAM_ASSEMBLED,
                Idea.Status.IN_PROGRESS,
            ),
        )
    return qs.order_by('-created_at')