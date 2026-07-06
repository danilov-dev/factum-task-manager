import logging

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.exceptions import ValidationError
from django.shortcuts import get_object_or_404, redirect
from django.views.generic import CreateView, ListView

from apps.ideas.forms.response_forms import ResponseCreateForm
from apps.ideas.models import Idea, IdeaRole, IdeaResponse
from apps.ideas.services.response import (
    create_response,
    approve_response,
    reject_response,
    cancel_response,
)

logger = logging.getLogger(__name__)


class ResponseCreateView(LoginRequiredMixin, CreateView):
    """Создание отклика на роль."""
    form_class = ResponseCreateForm
    template_name = 'ideas/responses/create_response.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        role_id = self.kwargs.get('role_id')
        role = get_object_or_404(
            IdeaRole.objects.select_related('idea', 'idea__author'),
            pk=role_id
        )
        context['role'] = role
        context['idea'] = role.idea
        return context

    def form_valid(self, form):
        role_id = self.kwargs.get('role_id')

        try:
            response = create_response(
                user=self.request.user,
                role_id=role_id,
                message=form.cleaned_data['message']
            )

            logger.info(
                "Пользователь %s оставил отклик на роль '%s' (идея: %s)",
                self.request.user, response.role.title, response.role.idea.title
            )

            messages.success(self.request, 'Ваш отклик успешно отправлен!')
            return redirect('ideas:detail', pk=response.role.idea.pk)

        except ValidationError as e:
            messages.error(self.request, str(e))
            return self.form_invalid(form)


class MyResponsesListView(LoginRequiredMixin, ListView):
    """Список моих откликов."""
    model = IdeaResponse
    template_name = 'ideas/responses/responses_list.html'
    context_object_name = 'responses'

    def get_queryset(self):
        status_filter = self.request.GET.get('status', 'pending')
        valid_statuses = ['all', 'pending', 'approved', 'rejected']

        if status_filter not in valid_statuses:
            status_filter = 'pending'

        qs = IdeaResponse.objects.for_user(self.request.user)

        if status_filter != 'all':
            qs = qs.by_status(status_filter)

        return qs.order_by('status', '-created_at')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        status_filter = self.request.GET.get('status', 'pending')
        valid_statuses = ['all', 'pending', 'approved', 'rejected']
        if status_filter not in valid_statuses:
            status_filter = 'pending'

        # Подсчет откликов по статусам
        all_responses = IdeaResponse.objects.for_user(self.request.user)
        context['counts'] = {
            'all': all_responses.count(),
            'pending': all_responses.pending().count(),
            'approved': all_responses.filter(status=IdeaResponse.Status.APPROVED).count(),
            'rejected': all_responses.filter(status=IdeaResponse.Status.REJECTED).count(),
        }
        context['current_status'] = status_filter

        return context


class IdeaResponsesListView(LoginRequiredMixin, ListView):
    """Список откликов на идею (для автора)."""
    model = IdeaResponse
    template_name = 'ideas/responses/responses_list.html'
    context_object_name = 'responses'

    def get_queryset(self):
        idea_id = self.kwargs.get('idea_id')
        idea = get_object_or_404(Idea, pk=idea_id, author=self.request.user)

        status_filter = self.request.GET.get('status', 'pending')
        valid_statuses = ['all', 'pending', 'approved', 'rejected']

        if status_filter not in valid_statuses:
            status_filter = 'pending'

        qs = IdeaResponse.objects.for_idea(idea)

        if status_filter != 'all':
            qs = qs.by_status(status_filter)

        return qs.order_by('status', '-created_at')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        idea_id = self.kwargs.get('idea_id')
        idea = get_object_or_404(Idea, pk=idea_id, author=self.request.user)

        status_filter = self.request.GET.get('status', 'pending')
        valid_statuses = ['all', 'pending', 'approved', 'rejected']
        if status_filter not in valid_statuses:
            status_filter = 'pending'

        # Подсчет откликов по статусам
        all_responses = IdeaResponse.objects.for_idea(idea)
        context['counts'] = {
            'all': all_responses.count(),
            'pending': all_responses.pending().count(),
            'approved': all_responses.filter(status=IdeaResponse.Status.APPROVED).count(),
            'rejected': all_responses.filter(status=IdeaResponse.Status.REJECTED).count(),
        }
        context['current_status'] = status_filter
        context['idea'] = idea

        return context


@login_required
def approve_response_view(request, response_id):
    """Одобрить отклик"""
    from django.http import JsonResponse

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
    from django.http import JsonResponse

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
    from django.http import JsonResponse

    if request.method != 'POST':
        return JsonResponse({'error': 'Method not allowed'}, status=405)

    try:
        cancel_response(response_id, request.user)
        logger.info("Пользователь %s отменил свой отклик (id=%d)", request.user, response_id)
        messages.success(request, 'Ваш отклик успешно отменен.')

    except (IdeaResponse.DoesNotExist, ValidationError) as e:
        messages.error(request, str(e))

    return redirect('ideas:responses:my_responses')