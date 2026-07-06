from django import template
from apps.subscriptions.services import is_subscribed

register = template.Library()

@register.filter(name='is_subscribed_by')
def is_subscribed_by(idea, user):
    return is_subscribed(user, idea)