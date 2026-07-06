from django.core.exceptions import PermissionDenied
from django.db import transaction

from apps.ideas.models import IdeaRole


@transaction.atomic
def delete_role(role: IdeaRole, user) -> int:
    """Удалить роль с проверкой прав."""
    if role.idea.author != user:
        raise PermissionDenied("Только автор идеи может удалять роли")

    responses_count = role.responses.count()
    role.delete()
    return responses_count