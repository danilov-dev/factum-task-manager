from django.core.exceptions import ValidationError
from django.db import transaction
from django.db.models import QuerySet
from django.shortcuts import get_object_or_404

from apps.ideas.models import IdeaResponse


def create_response(*, user, role_id: int, message: str = ''):
    """Создание отклика на роль"""
    from apps.ideas.models import IdeaRole

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

def _filter_responses_by_status(responses: QuerySet, status:str):
    """Фильтр queryset откликов по статусу"""
    if isinstance(status, list):
        responses = responses.filter(status__in=status)
    elif status != 'all':
        responses = responses.filter(status=status)
    return responses

def get_user_responses(user, status=None):
    """Получить все отклики пользователя"""
    qs = IdeaResponse.objects.filter(user=user).select_related(
        'role',
        'role__idea',
        'role__idea__author'
    )
    if  status:
        qs = _filter_responses_by_status(qs, status)

    return qs.order_by('status', '-created_at')


def get_responses_for_idea(idea, author, status=None):
    """Получить отклики на идею с опциональной фильтрацией по статусу"""
    if idea.author != author:
        raise ValidationError('Только автор идеи может просматривать отклики')

    qs = IdeaResponse.objects.filter(role__idea=idea).select_related('user', 'role')

    if status:
        qs = _filter_responses_by_status(qs, status)

    return qs.order_by('status', '-created_at')


def get_idea_responses_counts(idea, author):
    """Получить количество откликов по каждому статусу"""
    if idea.author != author:
        raise ValidationError('Только автор идеи может просматривать отклики')

    responses = IdeaResponse.objects.filter(role__idea=idea)
    return {
        'all': responses.count(),
        'pending': responses.filter(status=IdeaResponse.Status.PENDING).count(),
        'approved': responses.filter(status=IdeaResponse.Status.APPROVED).count(),
        'rejected': responses.filter(status=IdeaResponse.Status.REJECTED).count(),
    }

def get_user_responses_counts(user):
    responses = IdeaResponse.objects.filter(user=user)
    return {
        'all': responses.count(),
        'pending': responses.filter(status=IdeaResponse.Status.PENDING).count(),
        'approved': responses.filter(status=IdeaResponse.Status.APPROVED).count(),
        'rejected': responses.filter(status=IdeaResponse.Status.REJECTED).count(),
    }


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