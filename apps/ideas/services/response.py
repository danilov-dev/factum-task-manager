from django.core.exceptions import ValidationError
from django.db import transaction
from django.shortcuts import get_object_or_404

from apps.ideas.models import IdeaResponse, IdeaRole


@transaction.atomic
def create_response(*, user, role_id: int, message: str = ''):
    """Создание отклика на роль"""
    role = IdeaRole.objects.select_related('idea', 'idea__author').get(pk=role_id)

    if role.idea.author == user:
        raise ValidationError('Вы не можете откликнуться на свою идею')

    if not role.is_open:
        raise ValidationError('Набор на эту роль закрыт')

    if role.spots_left <= 0:
        raise ValidationError('Все места на эту роль уже заняты')

    if IdeaResponse.objects.filter(user=user, role=role).exists():
        raise ValidationError('Вы уже откликались на эту роль')

    response = IdeaResponse.objects.create(
        user=user,
        role=role,
        idea=role.idea,
        message=message,
        status=IdeaResponse.Status.PENDING
    )
    return response


@transaction.atomic
def approve_response(response_id: int, author):
    """Одобрить отклик"""
    response = IdeaResponse.objects.select_related(
        'role',
        'role__idea',
        'role__idea__author'
    ).get(pk=response_id)

    if response.role.idea.author != author:
        raise ValidationError('Только автор идеи может одобрять отклики')

    if response.status != IdeaResponse.Status.PENDING:
        raise ValidationError('Этот отклик уже обработан')

    if response.role.spots_left <= 0:
        raise ValidationError('Нет свободных мест на эту роль')

    response.status = IdeaResponse.Status.APPROVED
    response.save()

    response.role.count_filled += 1
    response.role.save(update_fields=['count_filled', 'is_open'])

    if response.role.spots_left == 0:
        response.role.is_open = False
        response.role.save()

    return response


@transaction.atomic
def reject_response(response_id: int, author):
    """Отклонить отклик"""
    response = IdeaResponse.objects.select_related(
        'role',
        'role__idea',
        'role__idea__author'
    ).get(pk=response_id)

    if response.role.idea.author != author:
        raise ValidationError('Только автор идеи может отклонять отклики')

    if response.status != IdeaResponse.Status.PENDING:
        raise ValidationError('Этот отклик уже обработан')

    response.status = IdeaResponse.Status.REJECTED
    response.save()

    return response


@transaction.atomic
def cancel_response(response_id: int, user):
    """Отменить (отозвать) отклик пользователем. Доступно только для статуса PENDING."""
    response = get_object_or_404(
        IdeaResponse.objects.select_related('role', 'role__idea'),
        pk=response_id,
        user=user
    )

    if response.status != IdeaResponse.Status.PENDING:
        raise ValidationError('Этот отклик уже обработан автором и не может быть отменен.')

    response.delete()