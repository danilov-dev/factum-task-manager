from django.core.exceptions import PermissionDenied
from django.db import transaction
from django.shortcuts import get_object_or_404

from apps.ideas.models import IdeaRole


def get_role(role_id: int):
    return get_object_or_404(
        IdeaRole.objects.prefetch_related(
            'necessary_skills',
            'necessary_skills__skill',
        ),
        pk=role_id,
    )

def get_all_roles(idea_id: int):
    roles = IdeaRole.objects.select_related('idea').prefetch_related(
        'necessary_skills__skill',
    ).filter(
        idea_id=idea_id
    )
    return roles


@transaction.atomic
def delete_role(role: IdeaRole, user) -> int:
    if role.idea.author != user:
        raise PermissionDenied(
            "Только автор идеи может удалять роли"
        )

    responses_count = role.responses.count()

    role.delete()

    return responses_count