from django.db import IntegrityError

from apps.ideas.models import Idea
from apps.likes.models import Like


def switch(user, idea=None):
    """Переключить лайк (если нет лайка - создает и наоборот"""
    filters = {'user':user}
    if idea:
        filters['idea'] = idea
        target_obj = idea
    else:
        raise ValueError('Идея должна быть указана')

    existing_like = Like.objects.filter(**filters).first()
    if existing_like:
        existing_like.delete()
        is_liked = False
    else:
        try:
            Like.objects.create(**filters)
            is_liked = True
        except IntegrityError:
            is_liked = False
    likes_count = target_obj.likes.count()
    return is_liked, likes_count

def is_liked(user, obj):
    """Проверка объекта на лайк пользователя"""
    if isinstance(obj, Idea):
        return Like.objects.filter(user=user,idea=obj).exists()
    return False