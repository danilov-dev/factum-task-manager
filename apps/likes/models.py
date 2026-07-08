from django.core.exceptions import ValidationError
from django.db import models


class Like(models.Model):

    user = models.ForeignKey(
        'users.User',
        on_delete=models.CASCADE,
        related_name='likes',
    )
    idea = models.ForeignKey(
        'ideas.Idea',
        on_delete=models.CASCADE,
        related_name='likes',
        null=True,
        blank=True,
    )
    post = models.ForeignKey(
        'posts.Post',
        on_delete=models.CASCADE,
        related_name='likes',
        null=True,
        blank=True,
    )

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'idea'],
                name='unique_like_on_idea',
                condition=models.Q(idea__isnull=False)
            ),
        ]
        ordering = ['-created_at']

    def clean(self):
        targets = [self.idea.id, self.post.id ]
        filled = sum(1 for t in targets if t is not None)
        if filled != 1:
            raise ValidationError(
                'Лайк должен быть привязан только к одной сущности'
            )

    @property
    def target(self):
        return self.idea or self.post

    def __str__(self):
        return f'{self.user} -> {self.target}'
