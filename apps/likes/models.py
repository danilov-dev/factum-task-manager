from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.db import models


class Like(models.Model):

    user = models.ForeignKey(
        'users.User',
        on_delete=models.CASCADE,
        related_name='likes',
    )

    content_type = models.ForeignKey(
        ContentType,
        on_delete=models.CASCADE,
        related_name='likes',
    )
    object_id = models.PositiveIntegerField()
    content_object = GenericForeignKey('content_type', 'object_id')
    value = models.SmallIntegerField(
        choices=[(1,'like'),(-1,'dislike')],
        default=1,
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'content_type', 'object_id'],
                name='unique_like_per_user_per_object',
            ),
        ]
        ordering = ['-created_at']
        indexes = [models.Index(fields=['content_type', 'object_id']),]

    def __str__(self):
        return f'{self.user} -> {self.content_object}'
