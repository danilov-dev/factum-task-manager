from django.urls import path
from apps.ideas.views.roles import create_role, get_skills_by_category

app_name = 'roles'

urlpatterns = [
    path('<int:pk>/create/', create_role, name='create_role'),
    path('api/skills-by-category/', get_skills_by_category, name='skills_by_category'),
    # path('<int:pk>/edit/', edit_role, name='edit'),
    # path('<int:pk>/', view_role, name='detail'),
]
