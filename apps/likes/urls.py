from django.urls import path

from apps.likes.views import switch_like

app_name = 'likes'

urlpatterns = [
    path('like/<str:content_type>/<int:object_id>/', switch_like, name='switch_like'),
]