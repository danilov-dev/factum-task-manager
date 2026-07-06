from apps.ideas.models import Idea


def create_idea(*, author, title, about, description, category):
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


def update_idea(*, idea, **kwargs):
    """Обновить идею через сервис."""
    if 'status' in kwargs:
        new_status = kwargs['status']
        if new_status in [Idea.Status.OPEN, Idea.Status.TEAM_ASSEMBLED, Idea.Status.IN_PROGRESS]:
            kwargs['is_published'] = True

    for field, value in kwargs.items():
        if hasattr(idea, field) and getattr(idea, field) != value:
            setattr(idea, field, value)

    idea.save(update_fields=kwargs.keys())
    return idea
