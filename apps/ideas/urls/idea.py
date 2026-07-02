from django.urls import path, include

from apps.ideas.views.ideas import IdeasList, create_new_idea, IdeaDetail, edit_idea

urlpatterns = [
    path('', IdeasList.as_view(), name='idea_list'),
    path('create/', create_new_idea, name='create'),
    path('<int:pk>/', IdeaDetail.as_view(), name='detail'),
    path('<int:pk>/edit/', edit_idea, name='edit'),
]
