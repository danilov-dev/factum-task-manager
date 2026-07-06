from django.db import models

from apps.users.models import User
from config import settings


class Subscription(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='subscriptions',
    )
    idea = models.ForeignKey(
        'ideas.Idea',
        on_delete=models.CASCADE,
        related_name='subscriptions',
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'subscriptions'
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'idea'],
                name='unique_user_idea_subscription',
            ),
        ]
        indexes = [
            models.Index(fields=['idea', 'user']),
            models.Index(fields=['user', '-created_at']),
        ]
        ordering = ['-created_at']

    def __str__(self):
        return f'{self.user} -> {self.idea}'

