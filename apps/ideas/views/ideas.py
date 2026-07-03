import logging

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import Http404
from django.shortcuts import redirect, render, get_object_or_404
from django.views.generic import ListView, DetailView

from apps.ideas.decorators import user_is_author_of_idea
from apps.ideas.forms import IdeaCreateForm
from apps.ideas.models import Idea, IdeaResponse
from apps.ideas.services.idea import get_visible_ideas, get_idea_with_stats, create_idea, update_idea
from apps.ideas.services.response import get_responses_for_idea, get_pending_responses_count

logger = logging.getLogger(__name__)

class IdeasList(ListView):
    model = Idea
    template_name = 'ideas/ideas/idea_list.html'
    context_object_name = 'ideas'

    def get_queryset(self):
        return get_visible_ideas()


class IdeaDetail(DetailView):
    model = Idea
    template_name = 'ideas/ideas/idea_detail.html'
    context_object_name = 'idea'

    def get_object(self, queryset=None):
        idea_id = self.kwargs.get('pk')
        if idea_id is None:
            raise Http404("Идея не найдена")
        return get_idea_with_stats(idea_id=idea_id)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        idea = self.object

        context['all_responses'] = get_responses_for_idea(idea, idea.author, ['approved','rejected']).count()
        if self.request.user.is_authenticated:
            context['pend_responses'] = get_pending_responses_count(idea)

        return context


@login_required
def create_new_idea(request):
    if request.method == 'POST':
        form = IdeaCreateForm(request.POST)
        if form.is_valid():
            idea = create_idea(
                author=request.user,
                title=form.cleaned_data['title'],
                about=form.cleaned_data['about'],
                description=form.cleaned_data['description'],
                category=form.cleaned_data['category'],
            )
            logger.info(
                'Создана идея "%s" (id=%d) пользователем %s',
                idea.title, idea.pk, request.user,
            )
            messages.success(request, f'Идея: {idea.title} успешно создана')
            return redirect('ideas:detail', pk=idea.pk)
    else:
        form = IdeaCreateForm()
    return render(request, 'ideas/ideas/create.html', {'form': form})


@login_required
@user_is_author_of_idea
def edit_idea(request, pk):
    idea = get_object_or_404(Idea, pk=pk)

    if request.method == 'POST':
        form = IdeaCreateForm(request.POST)
        if form.is_valid():
            idea = update_idea(
                idea=idea,
                title=form.cleaned_data['title'],
                about=form.cleaned_data['about'],
                description=form.cleaned_data['description'],
                category=form.cleaned_data['category'],
                status=form.cleaned_data['status'],
            )
            logger.info("Обновлена идея '%s' (id=%d) пользователем %s", idea.title, idea.pk, request.user)
            messages.success(request, f'Идея: {idea.title} успешно обновлена')
            return redirect('ideas:detail', pk=idea.pk)
    else:
        form = IdeaCreateForm(instance=idea)

    return render(request, 'ideas/ideas/create.html', {'form': form, 'idea': idea})