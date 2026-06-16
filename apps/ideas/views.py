from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404
from django.views.generic import ListView, DetailView
from .models import Idea
from .forms import IdeaCreateForm
from .services import get_visible_ideas, get_idea, create_idea, update_idea


class IdeasList(ListView):
    model = Idea
    template_name = 'ideas/idea_list.html'
    context_object_name = 'ideas'

    def get_queryset(self):
        return get_visible_ideas()


class IdeaDetail(DetailView):
    model = Idea
    template_name = 'ideas/idea_detail.html'
    context_object_name = 'idea'

    def get_object(self, queryset=None):
        idea_id = self.kwargs.get('pk')
        if idea_id is None:
            from django.http import Http404
            raise Http404("Идея не найдена")
        return get_idea(idea_id=idea_id)


@login_required
def create_new_idea(request):
    if request.method == 'POST':
        form = IdeaCreateForm(request.POST)
        if form.is_valid():
            idea = create_idea(
                author=request.user,
                title=form.cleaned_data['title'],
                description=form.cleaned_data['description'],
                category=form.cleaned_data['category'],
            )
            messages.success(request, f'Идея: {idea.title} успешно создана')
            return redirect('ideas:detail', pk=idea.pk)
    else:
        form = IdeaCreateForm()

    return render(request, 'ideas/create.html', {'form': form})


@login_required
def edit_idea(request, pk):
    idea = get_object_or_404(Idea, pk=pk)

    if request.user != idea.author:
        messages.error(request, 'Вы не можете редактировать чужую идею')
        return redirect('ideas:detail', pk=idea.pk)

    if request.method == 'POST':
        form = IdeaCreateForm(request.POST, instance=idea)
        if form.is_valid():
            update_idea(
                idea_id=pk,
                title=form.cleaned_data['title'],
                description=form.cleaned_data['description'],
                category=form.cleaned_data['category'],
            )
            messages.success(request, f'Идея: {idea.title} успешно обновлена')
            return redirect('ideas:detail', pk=idea.pk)
    else:
        form = IdeaCreateForm(instance=idea)

    return render(request, 'ideas/edit.html', {'form': form, 'idea': idea})