from django.contrib.contenttypes.models import ContentType
from django.db import transaction
from django.db.models import Count, Q

from apps.likes.models import Like


@transaction.atomic
def switch(user, obj, value):
    """Переключить лайк/дизлайк"""
    content_type = ContentType.objects.get_for_model(obj)

    # Ищем ЛЮБУЮ существующую реакцию (без фильтрации по value)
    existing_like = Like.objects.filter(
        user=user,
        content_type=content_type,
        object_id=obj.pk
    ).first()

    if existing_like:
        if existing_like.value == value:
            # Пользователь нажал на ту же кнопку - удаляем реакцию
            existing_like.delete()
            new_value = None
        else:
            # Пользователь переключился с лайка на дизлайк или наоборот
            existing_like.value = value
            existing_like.save()
            new_value = value
    else:
        # Создаем новую реакцию
        Like.objects.create(
            user=user,
            content_type=content_type,
            object_id=obj.pk,
            value=value
        )
        new_value = value

    # Считаем лайки и дизлайки
    stats = Like.objects.filter(
        content_type=content_type,
        object_id=obj.pk
    ).aggregate(
        likes_count=Count('id', filter=Q(value=1)),
        dislikes_count=Count('id', filter=Q(value=-1))
    )

    return new_value, stats['likes_count'], stats['dislikes_count']


def is_liked(user, obj):
    """Проверка, поставил ли пользователь ЛАЙК (value=1)"""
    if not user.is_authenticated:
        return False

    content_type = ContentType.objects.get_for_model(obj)

    return Like.objects.filter(
        user=user,
        content_type=content_type,
        object_id=obj.pk,
        value=1
    ).exists()


def get_user_reaction(user, obj):
    """
    Получить реакцию пользователя на объект

    Returns:
        int or None: 1 если лайк, -1 если дизлайк, None если нет реакции
    """
    if not user.is_authenticated:
        return None

    content_type = ContentType.objects.get_for_model(obj)

    like = Like.objects.filter(
        user=user,
        content_type=content_type,
        object_id=obj.pk
    ).first()

    return like.value if like else None