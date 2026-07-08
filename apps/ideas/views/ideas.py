import logging

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.exceptions import PermissionDenied
from django.http import Http404, HttpResponseNotAllowed
from django.shortcuts import get_object_or_404, render
from django.urls import reverse_lazy, reverse
from django.views.generic import ListView, DetailView, CreateView, UpdateView

from apps.ideas.decorators import user_is_author_of_idea
from apps.ideas.forms import IdeaCreateForm
from apps.ideas.models import Idea
from apps.ideas.services.idea import create_idea, update_idea
from apps.likes.services import switch
from apps.likes.utils import annotate_queryset_likes, annotate_object_likes

logger = logging.getLogger(__name__)


class IdeasList(ListView):
    """Список всех видимых идей."""
    model = Idea
    template_name = 'ideas/ideas/idea_list.html'
    context_object_name = 'ideas'

    def get_queryset(self):
        ideas = Idea.objects.visible()

        search_query = self.request.GET.get('q', '').strip()
        if search_query:
            from django.db.models import Q
            ideas = ideas.filter(
                Q(title__icontains=search_query) |
                Q(about__icontains=search_query)
            )
        return annotate_queryset_likes(queryset=ideas, user=self.request.user, model_name='idea')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['search_query'] = self.request.GET.get('q', '')
        return context

    def render_to_response(self, context, **response_kwargs):
        # Если это HTMX-запрос, возвращаем только partial
        if self.request.headers.get('HX-Request'):
            return self.response_class(
                request=self.request,
                template='/partials/_idea_list.html',
                context=context,
                using=self.template_engine,
                **response_kwargs
            )
        return super().render_to_response(context, **response_kwargs)


class IdeaDetail(DetailView):
    """Детальная страница идеи."""
    model = Idea
    template_name = 'ideas/ideas/idea_detail.html'
    context_object_name = 'idea'


    def get_object(self, queryset=None):

        idea = get_object_or_404(Idea, pk=self.kwargs['pk'])
        idea = annotate_object_likes(idea, self.request.user, 'idea')

        idea.open_roles_count = sum(1 for role in idea.roles.all() if role.is_open)
        idea.has_team = any(role.count_filled > 0 for role in idea.roles.all())
        idea.search_pronoun = 'Мы ищем' if idea.has_team else 'Я ищу'

        return idea

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        idea = self.object

        # Количество одобренных/отклоненных откликов
        context['all_responses'] = idea.responses.filter(
            status__in=['approved', 'rejected']
        ).count()

        context['likes_count'] = idea.likes_count

        if self.request.user.is_authenticated:
            # Количество откликов на рассмотрении
            context['pend_responses'] = idea.responses.pending().count()

        return context


class IdeaCreateView(LoginRequiredMixin, CreateView):
    model = Idea
    form_class = IdeaCreateForm
    template_name = 'ideas/ideas/create.html'

    def form_valid(self, form):
        idea = create_idea(
            author=self.request.user,
            title=form.cleaned_data['title'],
            about=form.cleaned_data['about'],
            description=form.cleaned_data['description'],
            category=form.cleaned_data['category'],
        )

        logger.info('Создана идея "%s" (id=%d) пользователем %s',
                    idea.title, idea.pk, self.request.user)

        messages.success(self.request, f'Идея: {idea.title} успешно создана')
        return super().form_valid(form)

    def get_success_url(self):
        return reverse_lazy('ideas:detail', kwargs={'pk': self.object.pk})


class IdeaUpdateView(LoginRequiredMixin, UpdateView):
    model = Idea
    form_class = IdeaCreateForm
    template_name = 'ideas/ideas/create.html'
    context_object_name = 'idea'

    def get_object(self, queryset=None):
        idea = get_object_or_404(Idea, pk=self.kwargs['pk'])
        if idea.author != self.request.user:
            raise PermissionDenied("Только автор может редактировать")
        return idea

    def form_valid(self, form):
        self.object = update_idea(
            idea=self.object,
            title=form.cleaned_data['title'],
            about=form.cleaned_data['about'],
            description=form.cleaned_data['description'],
            category=form.cleaned_data['category'],
            status=form.cleaned_data.get('status', self.object.status),
            is_published=form.cleaned_data.get('is_published', self.object.is_published),
        )

        messages.success(self.request, f'Идея: {self.object.title} обновлена')
        return super().form_valid(form)

    def get_success_url(self):
        return reverse('ideas:detail', kwargs={'pk': self.object.pk})


# @login_required
# def switch_idea_like(request, idea_id):
#     if request.method != 'POST':
#         return HttpResponseNotAllowed(['POST'])
#
#     idea = get_object_or_404(Idea, pk=idea_id)
#     is_liked, likes_count = switch(request.user, idea)
#
#     return render(request, 'partials/like_button.html', {
#         'idea': idea,
#         'likes_count': likes_count,
#         'is_liked': is_liked,
#     })
