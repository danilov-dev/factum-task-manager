from django.urls import path

from apps.subscriptions.views import switch_subscription

app_name = 'subscriptions'

urlpatterns = [
    path('ideas/<int:idea_id>/subscribe/', switch_subscription, name='switch')
]