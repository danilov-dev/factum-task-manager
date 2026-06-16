from django.urls import path

from apps.ideas.views import IdeasList, create_new_idea, IdeaDetail, edit_idea

app_name = 'ideas'

urlpatterns = [
    path('', IdeasList.as_view(), name='idea_list'),
    path('create/', create_new_idea, name='create'),
    path('<int:pk>/', IdeaDetail.as_view(), name='detail'),
    path('<int:pk>/edit/', edit_idea, name='edit'),  # URL для редактирования
]
