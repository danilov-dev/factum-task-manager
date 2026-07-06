# from django.db import models
# from django.db.models.signals import post_save, post_delete
# from django.dispatch import receiver
#
# from apps.subscriptions.models import Subscription
#
#
# @receiver(post_save, sender=Subscription)
# def increment_sub_count(sender, instance, created, **kwargs):
#     """Сигнал на увеличения счетчика подписок на идею """
#     if created:
#         instance.idea.__class__.objects.filter(pk=instance.idea.pk).update(
#             subscribers_count=models.F('subscribers_count') + 1
#         )
#
#
# @receiver(post_delete, sender=Subscription)
# def decrement_sub_count(sender, instance, **kwargs):
#     """Сигнал на уменьшение счетчика подписок на идею """
#     instance.idea.__class__.objects.filter(pk=instance.idea.pk).update(
#         subscribers_count=models.F('subscribers_count') - 1
#     )
