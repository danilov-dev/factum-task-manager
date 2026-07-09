from django.contrib.contenttypes.models import ContentType
from django.db.models import Count, OuterRef, Exists, Value, BooleanField, Q, ExpressionWrapper, F, IntegerField, \
    Subquery

from apps.likes.models import Like


def annotate_queryset_likes(queryset, user=None):
    """
    Универсальная функция для аннотации лайков/дизлайков через GenericForeignKey.

    Аннотирует queryset следующими полями:
    - likes_count: количество лайков (value=1)
    - dislikes_count: количество дизлайков (value=-1)
    - score: разница между лайками и дизлайками
    - user_reaction: реакция пользователя (1, -1 или None)

    Args:
        queryset: QuerySet модели (Idea, Post, etc.)
        user: Пользователь (опционально)

    Returns:
        QuerySet с аннотациями
    """

    # Получаем ContentType для модели в queryset
    model = queryset.model
    content_type = ContentType.objects.get_for_model(model)

    # Аннотируем количество лайков и дизлайков
    qs = queryset.annotate(
        likes_count=Count(
            'likes',
            filter=Q(likes__value=1, likes__content_type=content_type)
        ),
        dislikes_count=Count(
            'likes',
            filter=Q(likes__value=-1, likes__content_type=content_type)
        ),
        score=ExpressionWrapper(
            F('likes_count') - F('dislikes_count'),
            output_field=IntegerField()
        )
    )

    # Аннотируем реакцию пользователя
    if user and user.is_authenticated:
        user_likes = Like.objects.filter(
            user=user,
            content_type=content_type,
            object_id=OuterRef('pk')
        )
        qs = qs.annotate(
            user_reaction=Subquery(user_likes.values('value')[:1])
        )
    else:
        qs = qs.annotate(
            user_reaction=Value(None, output_field=IntegerField())
        )

    return qs


def annotate_object_likes(obj, user=None):
    """
    Аннотирует один объект данными о лайках/дизлайках.

    Добавляет к объекту атрибуты:
    - likes_count: количество лайков
    - dislikes_count: количество дизлайков
    - score: разница между лайками и дизлайками
    - user_reaction: реакция пользователя (1, -1 или None)

    Args:
        obj: Экземпляр модели (Idea, Post, etc.)
        user: Пользователь (опционально)

    Returns:
        Объект с аннотациями
    """
    content_type = ContentType.objects.get_for_model(obj)

    # Считаем лайки и дизлайки одним запросом
    stats = Like.objects.filter(
        content_type=content_type,
        object_id=obj.pk
    ).aggregate(
        likes_count=Count('id', filter=Q(value=1)),
        dislikes_count=Count('id', filter=Q(value=-1))
    )

    obj.likes_count = stats['likes_count']
    obj.dislikes_count = stats['dislikes_count']
    obj.score = obj.likes_count - obj.dislikes_count

    # Проверяем реакцию пользователя
    if user and user.is_authenticated:
        user_like = Like.objects.filter(
            user=user,
            content_type=content_type,
            object_id=obj.pk
        ).first()
        obj.user_reaction = user_like.value if user_like else None
    else:
        obj.user_reaction = None

    return obj
