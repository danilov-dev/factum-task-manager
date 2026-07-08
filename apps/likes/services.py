
from apps.ideas.models import Idea
from apps.likes.models import Like
from apps.posts.models import Post


def switch(user, obj):
    """Переключить лайк (если нет лайка - создает и наоборот)"""

    if isinstance(obj, Idea):
        field_name = 'idea'
    elif isinstance(obj, Post):
        field_name = 'post'
    else:
        raise ValueError('Unsupported object type')

    existing_like = Like.objects.filter(
        user=user,
        **{field_name: obj}
    ).first()

    if existing_like:
        existing_like.delete()
        is_liked = False
    else:
        Like.objects.create(
            user=user,
            **{field_name: obj}
        )
        is_liked = True

    likes_count = Like.objects.filter(
        **{field_name: obj}
    ).count()

    return is_liked, likes_count


def is_liked(user, obj):
    """Проверка объекта на лайк пользователя"""
    if not user.is_authenticated:
        return False

    if isinstance(obj, Idea):
        return Like.objects.filter(user=user, idea=obj).exists()
    elif isinstance(obj, Post):
        return Like.objects.filter(user=user, post=obj).exists()
    return False