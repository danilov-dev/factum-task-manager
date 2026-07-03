from functools import wraps

from django.contrib import messages
from django.shortcuts import get_object_or_404, redirect

from apps.ideas.models import Idea


def user_is_author_of_idea(view_func):
    """Декоратор проверки пользователя на авторство идеи"""

    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        idea_id = kwargs.get('pk') or kwargs.get('idea_id') or kwargs.get('id')
        idea = get_object_or_404(Idea, pk=idea_id)
        if request.user != idea.author:
            messages.error(request, 'У вас нет прав')
            return redirect('ideas:detail', pk=idea.pk)
        return view_func(request, *args, **kwargs)

    return wrapper
