from django.urls import path, include

from apps.ideas.views.ideas import (
    IdeasList,
    IdeaDetail,
    IdeaCreateView,
    IdeaUpdateView
)

urlpatterns = [
    path('', IdeasList.as_view(), name='idea_list'),
    path('create/', IdeaCreateView.as_view(), name='create'),
    path('<int:idea_id>/', IdeaDetail.as_view(), name='detail'),
    path('<int:idea_id>/edit/', IdeaUpdateView.as_view(), name='edit'),
]
