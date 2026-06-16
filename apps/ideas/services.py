from django.shortcuts import get_object_or_404

from apps.ideas.models import Idea


def create_idea(*, author, title, description, category):
    """
    Создать черновик идеи.
    """
    idea = Idea.objects.create(
        author=author,
        title=title,
        description=description,
        category=category,
        status=Idea.Status.DRAFT,
        is_published=False,
    )
    return idea

def update_idea(*, idea_id, title, description, category):
    """Обновить существующую идею."""
    idea = get_object_or_404(Idea, pk=idea_id)
    idea.title = title
    idea.description = description
    idea.category = category
    idea.save()
    return idea

def get_idea(*, idea_id: int):
    return get_object_or_404(Idea, pk=idea_id)


def get_visible_ideas():
    """Возвращает идей, видимых в публичной ленте"""
    return Idea.objects.filter(
        is_published=True,
        status__in=(Idea.Status.OPEN, Idea.Status.TEAM_ASSEMBLED, Idea.Status.IN_PROGRESS)
    ).select_related('author').prefetch_related('roles')


def get_ideas_by_category(category: str):
    """Возвращает идеи по категории"""
    return get_visible_ideas().filter(category=category)
