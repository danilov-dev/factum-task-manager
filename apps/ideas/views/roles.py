from collections import defaultdict

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import  JsonResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.views.decorators.http import require_GET

from apps.ideas.forms import RoleCreateForm, RoleSkillFormSet
from apps.ideas.models import Idea
from apps.users.models import Skill


@login_required
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

            messages.success(request, f'Роль "{role.title}" успешно создана!')
            return redirect('ideas:detail', pk=idea.id)
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
    return render(request, 'ideas/create_role.html', context)


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