import logging
from collections import defaultdict

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db import transaction
from django.http import JsonResponse, Http404
from django.shortcuts import render, redirect, get_object_or_404
from django.views.decorators.http import require_GET
from django.views.generic import DetailView, ListView, DeleteView

from apps.ideas.forms import RoleCreateForm, RoleSkillFormSet
from apps.ideas.models import Idea, IdeaRole
from apps.ideas.services.role import get_role, get_all_roles, delete_role
from apps.users.models import Skill

logger = logging.getLogger(__name__)


class RoleDetailView(DetailView):
    model = IdeaRole
    template_name = 'ideas/roles/role_detail.html'
    context_object_name = 'role'

    def get_object(self, queryset=None):
        role_id = self.kwargs.get('role_id')
        if role_id is None:
            raise Http404('Роль не найдена')
        return get_role(role_id=role_id)


@login_required
@transaction.atomic
def create_role(request, pk):
    idea = get_object_or_404(Idea, id=pk)
    if request.user != idea.author:
        messages.error(request, 'Вы не можете добавлять роли к этой инициативе')
        return redirect('ideas:detail', pk=idea.id)

    skills_by_category = defaultdict(list)
    for skill in Skill.objects.all().order_by('category', 'name'):
        skills_by_category[skill.category].append({
            'id': skill.id,
            'name': skill.name,
            'category': skill.category,
        })

    skills_data = dict(skills_by_category)

    if request.method == 'POST':
        form = RoleCreateForm(request.POST, idea=idea)
        formset = RoleSkillFormSet(request.POST, instance=None)

        if form.is_valid() and formset.is_valid():
            role = form.save()
            formset.instance = role
            formset.save()
            logger.info("Создана роль '%s' для идеи '%s' (id=%d)", role.title, idea.title, idea.pk)
            messages.success(request, f'Роль "{role.title}" успешно создана!')
            return redirect('ideas:detail', pk=idea.pk)
    else:
        form = RoleCreateForm(idea=idea)
        formset = RoleSkillFormSet(instance=None)

    context = {
        'form': form,
        'formset': formset,
        'idea': idea,
        'title': f'Создание роли для "{idea.title}"',
        'skills_data': skills_data,
        'category_choices': dict(Skill.Category.choices),
    }
    return render(request, 'ideas/roles/create_role.html', context)


@login_required
@require_GET
def get_skills_by_category(request):
    """API для получения навыков по категории."""
    try:
        category = request.GET.get('category', '').strip()
        if not category:
            return JsonResponse({
                'skills': [],
                'error': 'Категория не указана',
            }, status=400)

        skills = Skill.objects.filter(category=category).values('id', 'name')

        return JsonResponse({
            'skills': list(skills),
            'count': skills.count(),
        })

    except Exception as e:
        return JsonResponse({
            'skills': [],
            'error': str(e),
        }, status=500)


class RolesListView(ListView):
    model = IdeaRole
    template_name = 'ideas/roles/role_list.html'
    context_object_name = 'roles'

    def get_queryset(self):
        idea_id = self.kwargs.get('idea_id')
        return get_all_roles(idea_id)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        idea_id = self.kwargs.get('idea_id')

        context['idea'] = get_object_or_404(Idea, pk=idea_id)
        context['idea_id'] = idea_id

        return context


class DeleteRoleView(LoginRequiredMixin, DeleteView):
    model = IdeaRole
    template_name = 'ideas/roles/role_confirm_delete.html'
    pk_url_kwarg = 'role_id'
    context_object_name = 'role'

    def form_valid(self, form):
        idea_id = self.object.idea_id
        role_title = self.object.title

        deleted_responses = delete_role(self.object, self.request.user)
        logger.info("Удалена роль '%s' (idea_id=%d) пользователем %s", role_title, idea_id, self.request.user)
        if deleted_responses:
            messages.warning(self.request, f"Удалено {deleted_responses} откликов.")
        else:
            messages.success(self.request, f"Роль {role_title} удалена.")

        return redirect('ideas:detail', pk=idea_id)


@login_required
@transaction.atomic
def edit_role(request, role_id):
    role = get_object_or_404(IdeaRole, pk=role_id)
    idea = role.idea

    if request.user != idea.author:
        messages.error(request, 'Вы не можете редактировать эту роль')
        return redirect('ideas:detail', pk=idea.id)

    skills_by_category = defaultdict(list)
    for skill in Skill.objects.all().order_by('category', 'name'):
        skills_by_category[skill.category].append({
            'id': skill.pk,
            'name': skill.name,
            'category': skill.category,
        })

    if request.method == 'POST':
        form = RoleCreateForm(request.POST, instance=role, idea=idea)
        formset = RoleSkillFormSet(request.POST, instance=role)

        if form.is_valid() and formset.is_valid():
            role = form.save()
            formset.save()
            logger.info("Обновлена роль '%s' (id=%d)", role.title, role.pk)
            messages.success(request, f'Роль "{role.title}" успешно обновлена!')
            return redirect('ideas:detail', pk=idea.id)
    else:
        form = RoleCreateForm(instance=role, idea=idea)
        formset = RoleSkillFormSet(instance=role)

    context = {
        'form': form,
        'formset': formset,
        'idea': idea,
        'role': role,
        'title': f'Редактирование роли "{role.title}"',
        'skills_data': dict(skills_by_category),
        'category_choices': dict(Skill.Category.choices),
        'is_edit': True,
    }
    return render(request, 'ideas/roles/create_role.html', context)
