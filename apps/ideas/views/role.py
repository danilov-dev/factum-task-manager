import logging
from collections import defaultdict

from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db import transaction
from django.http import JsonResponse, Http404
from django.shortcuts import get_object_or_404, redirect
from django.views.generic import DetailView, ListView, DeleteView, CreateView, UpdateView

from apps.ideas.forms import RoleCreateForm, RoleSkillFormSet
from apps.ideas.models import Idea, IdeaRole
from apps.ideas.services.role import delete_role
from apps.users.models import Skill

logger = logging.getLogger(__name__)


class RoleDetailView(DetailView):
    """Детальная страница роли."""
    model = IdeaRole
    template_name = 'ideas/roles/role_detail.html'
    context_object_name = 'role'
    pk_url_kwarg = 'role_id'

    def get_object(self, queryset=None):
        role_id = self.kwargs.get('role_id')
        if role_id is None:
            raise Http404('Роль не найдена')

        return get_object_or_404(
            IdeaRole.objects.with_details(),
            pk=role_id
        )


class RolesListView(ListView):
    """Список ролей для идеи."""
    model = IdeaRole
    template_name = 'ideas/roles/role_list.html'
    context_object_name = 'roles'

    def get_queryset(self):
        idea_id = self.kwargs.get('idea_id')
        return IdeaRole.objects.for_idea(idea_id)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        idea_id = self.kwargs.get('idea_id')
        context['idea'] = get_object_or_404(Idea, pk=idea_id)
        context['idea_id'] = idea_id
        return context


class RoleCreateView(LoginRequiredMixin, CreateView):
    """Создание новой роли."""
    model = IdeaRole
    form_class = RoleCreateForm
    template_name = 'ideas/roles/create_role.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        idea_id = self.kwargs.get('pk')
        idea = get_object_or_404(Idea, id=idea_id)

        # Проверка прав
        if self.request.user != idea.author:
            messages.error(self.request, 'Вы не можете добавлять роли к этой инициативе')
            return redirect('ideas:detail', pk=idea.id)

        # Подготовка данных для навыков
        skills_by_category = defaultdict(list)
        for skill in Skill.objects.all().order_by('category', 'name'):
            skills_by_category[skill.category].append({
                'id': skill.id,
                'name': skill.name,
                'category': skill.category,
            })

        context['formset'] = RoleSkillFormSet(self.request.POST or None)
        context['idea'] = idea
        context['title'] = f'Создание роли для "{idea.title}"'
        context['skills_data'] = dict(skills_by_category)
        context['category_choices'] = dict(Skill.Category.choices)

        return context

    def form_valid(self, form):
        idea_id = self.kwargs.get('pk')
        idea = get_object_or_404(Idea, id=idea_id)

        formset = RoleSkillFormSet(self.request.POST)

        if form.is_valid() and formset.is_valid():
            with transaction.atomic():
                role = form.save(commit=False)
                role.idea = idea
                role.save()
                formset.instance = role
                formset.save()

            logger.info("Создана роль '%s' для идеи '%s' (id=%d)",
                        role.title, idea.title, idea.pk)
            messages.success(self.request, f'Роль "{role.title}" успешно создана!')
            return redirect('ideas:detail', pk=idea.pk)

        return self.form_invalid(form)


class RoleUpdateView(LoginRequiredMixin, UpdateView):
    """Редактирование роли."""
    model = IdeaRole
    form_class = RoleCreateForm
    template_name = 'ideas/roles/create_role.html'
    context_object_name = 'role'
    pk_url_kwarg = 'role_id'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        role = self.get_object()
        idea = role.idea

        # Проверка прав
        if self.request.user != idea.author:
            messages.error(self.request, 'Вы не можете редактировать эту роль')
            return redirect('ideas:detail', pk=idea.id)

        # Подготовка данных для навыков
        skills_by_category = defaultdict(list)
        for skill in Skill.objects.all().order_by('category', 'name'):
            skills_by_category[skill.category].append({
                'id': skill.pk,
                'name': skill.name,
                'category': skill.category,
            })

        context['formset'] = RoleSkillFormSet(self.request.POST or None, instance=role)
        context['idea'] = idea
        context['role'] = role
        context['title'] = f'Редактирование роли "{role.title}"'
        context['skills_data'] = dict(skills_by_category)
        context['category_choices'] = dict(Skill.Category.choices)
        context['is_edit'] = True

        return context

    def form_valid(self, form):
        role = self.get_object()
        idea = role.idea

        formset = RoleSkillFormSet(self.request.POST, instance=role)

        if form.is_valid() and formset.is_valid():
            with transaction.atomic():
                role = form.save()
                formset.save()

            logger.info("Обновлена роль '%s' (id=%d)", role.title, role.pk)
            messages.success(self.request, f'Роль "{role.title}" успешно обновлена!')
            return redirect('ideas:detail', pk=idea.id)

        return self.form_invalid(form)


class DeleteRoleView(LoginRequiredMixin, DeleteView):
    """Удаление роли."""
    model = IdeaRole
    template_name = 'ideas/roles/role_confirm_delete.html'
    pk_url_kwarg = 'role_id'
    context_object_name = 'role'

    def form_valid(self, form):
        idea_id = self.object.idea_id
        role_title = self.object.title

        deleted_responses = delete_role(self.object, self.request.user)

        logger.info("Удалена роль '%s' (idea_id=%d) пользователем %s",
                    role_title, idea_id, self.request.user)

        if deleted_responses:
            messages.warning(self.request, f"Удалено {deleted_responses} откликов.")
        else:
            messages.success(self.request, f"Роль {role_title} удалена.")

        return redirect('ideas:detail', pk=idea_id)


# FBV для API (не CRUD, а получение данных)
def get_skills_by_category(request):
    """API для получения навыков по категории."""
    from django.views.decorators.http import require_GET

    if request.method != 'GET':
        return JsonResponse({'error': 'Method not allowed'}, status=405)

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