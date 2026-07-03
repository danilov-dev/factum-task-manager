import logging

from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.exceptions import ValidationError
from django.http import JsonResponse

from ..models import Idea, IdeaRole, IdeaResponse
from ..forms.response_forms import ResponseCreateForm
from ..services.response import (
    create_response,
    get_user_responses,
    get_responses_for_idea,
    approve_response,
    reject_response, get_idea_responses_counts, cancel_response, get_user_responses_counts
)

logger = logging.getLogger(__name__)


@login_required
def create_response_view(request, role_id):
    """Создание отклика на роль"""
    role = get_object_or_404(
        IdeaRole.objects.select_related('idea', 'idea__author'),
        pk=role_id
    )

    if request.method == 'POST':
        form = ResponseCreateForm(request.POST)
        if form.is_valid():
            try:
                response = create_response(
                    user=request.user,
                    role_id=role_id,
                    message=form.cleaned_data['message']
                )

                logger.info("Пользователь %s оставил отклик на роль '%s' (идея: %s)",
                            request.user, role.title, role.idea.title)

                messages.success(request, 'Ваш отклик успешно отправлен!')
                return redirect('ideas:detail', pk=role.idea.pk)
            except ValidationError as e:
                messages.error(request, str(e))
    else:
        form = ResponseCreateForm()

    return render(request, 'ideas/responses/create_response.html', {
        'form': form,
        'role': role,
        'idea': role.idea
    })


def _validate_status(status: str):
    valid_statuses = ['all', 'pending', 'approved', 'rejected']
    if status not in valid_statuses:
        status = 'pending'
    return status


@login_required
def my_responses(request):
    """Список моих откликов"""
    status_filter = request.GET.get('status', 'pending')

    status_filter = _validate_status(status_filter)

    counts = get_user_responses_counts(request.user)

    responses = get_user_responses(request.user, status=status_filter)
    return render(request, 'ideas/responses/responses_list.html', {
        'responses': responses,
        'counts': counts,
        'current_status': status_filter,
    })


@login_required
def idea_responses(request, idea_id):
    """Список откликов на идею (для автора) с фильтрацией по статусу"""
    idea = get_object_or_404(Idea, pk=idea_id, author=request.user)
    status_filter = request.GET.get('status', 'pending')

    status_filter = _validate_status(status_filter)

    responses = get_responses_for_idea(idea, request.user, status=status_filter)

    counts = get_idea_responses_counts(idea, request.user)

    return render(request, 'ideas/responses/responses_list.html', {
        'idea': idea,
        'responses': responses,
        'counts': counts,
        'current_status': status_filter,
    })


@login_required
def approve_response_view(request, response_id):
    """Одобрить отклик"""
    if request.method != 'POST':
        return JsonResponse({'error': 'Method not allowed'}, status=405)

    try:
        response = approve_response(response_id, request.user)

        logger.info("Автор %s одобрил отклик пользователя %s", request.user, response.user)

        messages.success(request, f'Отклик от {response.user.username} одобрен!')

        return redirect('ideas:responses:idea_responses', idea_id=response.role.idea.pk)
    except (IdeaResponse.DoesNotExist, ValidationError) as e:
        messages.error(request, str(e))
        return redirect('ideas:idea_list')


@login_required
def reject_response_view(request, response_id):
    """Отклонить отклик"""
    if request.method != 'POST':
        return JsonResponse({'error': 'Method not allowed'}, status=405)

    try:
        response = reject_response(response_id, request.user)

        logger.info("Автор %s отклонил отклик пользователя %s", request.user, response.user)

        messages.success(request, f'Отклик от {response.user.username} отклонён')

        return redirect('ideas:responses:idea_responses', idea_id=response.role.idea.pk)
    except (IdeaResponse.DoesNotExist, ValidationError) as e:
        messages.error(request, str(e))
        return redirect('ideas:idea_list')


@login_required
def cancel_response_view(request, response_id):
    """Отмена отклика самим пользователем"""
    if request.method != 'POST':
        return JsonResponse({'error': 'Method not allowed'}, status=405)

    try:
        cancel_response(response_id, request.user)

        logger.info("Пользователь %s отменил свой отклик (id=%d)", request.user, response_id)

        messages.success(request, 'Ваш отклик успешно отменен.')
    except (IdeaResponse.DoesNotExist, ValidationError) as e:
        messages.error(request, str(e))

    return redirect('ideas:responses:responses_list')
