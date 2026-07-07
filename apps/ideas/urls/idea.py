from django.urls import path, include

from apps.ideas.views.ideas import (
    IdeasList,
    IdeaDetail,
    IdeaCreateView,
    IdeaUpdateView, switch_idea_like
)

urlpatterns = [
    path('', IdeasList.as_view(), name='idea_list'),
    path('create/', IdeaCreateView.as_view(), name='create'),
    path('<int:pk>/', IdeaDetail.as_view(), name='detail'),
    path('<int:pk>/edit/', IdeaUpdateView.as_view(), name='edit'),
    path('<int:idea_id>/like/', switch_idea_like, name='switch_like'),
]
