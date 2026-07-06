from django.db.models import Count, OuterRef, Exists, Value, BooleanField

from apps.likes.models import Like


def annotate_queryset_likes(queryset, user=None, model_name='idea'):
    """
    Универсальная функция для аннотации лайков.

    Args:
        queryset: QuerySet модели
        user: Пользователь
        model_name: Имя поля в Like модели ('idea', 'post', 'comment', etc)
    """
    qs = queryset.annotate(likes_count=Count('likes'))

    if user and user.is_authenticated:
        user_likes = Like.objects.filter(
            user=user,
            **{model_name: OuterRef('pk')}
        )
        qs = qs.annotate(is_liked=Exists(user_likes))
    else:
        qs = qs.annotate(is_like=Value(False, output_field=BooleanField()))

    return qs


def annotate_object_likes(obj, user=None, model_name='idea'):
    """
    Аннотирует один объект данными о лайках.

    Args:
        obj: Экземпляр модели
        user: Пользователь
        model_name: Имя поля в Like модели ('idea', 'post', 'comment', etc)
    """
    obj.likes_count = obj.likes.count()

    if user and user.is_authenticated:
        obj.is_liked = Like.objects.filter(
            user=user,
            **{model_name: obj}
        ).exists()
    else:
        obj.is_liked = False

    return obj