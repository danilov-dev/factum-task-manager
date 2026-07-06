from django.contrib.auth import get_user_model
from django.db import transaction

from apps.subscriptions.models import Subscription
from apps.users.models import User


class SubscriptionError(Exception):
    pass


def subscribe(user, idea):
    """Подписать пользователя. Возвращает True, если подписка создана."""
    if idea.author == user:
        raise SubscriptionError('Автор не может подписаться на свою идею')

    _, created = Subscription.objects.get_or_create(user=user, idea=idea)
    return created


def unsubscribe(user, idea):
    """Отписать. Возвращает True, если подписка была удалена."""
    deleted_count, _ = Subscription.objects.filter(user=user, idea=idea).delete()
    return deleted_count > 0

def switch(user, idea):
    """Переключает подписку"""
    with transaction.atomic():
        if is_subscribed(user, idea):
            unsubscribe(user, idea)
            return False
        subscribe(user, idea)
        return True

def is_subscribed(user, idea):
    """Проверяет подписан пользователь на идею или нет"""
    if not user.is_authenticated:
        return False
    return Subscription.objects.filter(user=user, idea=idea).exists()

def get_subscribers(idea):
    return User.objects.filter(
        subscriptions__idea=idea
    ).select_related('user')
