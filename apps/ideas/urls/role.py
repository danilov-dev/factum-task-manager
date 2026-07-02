from django.urls import path
from apps.ideas.views.role import create_role, get_skills_by_category, RoleDetailView, RolesListView, \
    DeleteRoleView, edit_role

app_name = 'roles'

urlpatterns = [
    path('<int:pk>/create/', create_role, name='create_role'),
    path('api/skills-by-category/', get_skills_by_category, name='skills_by_category'),
    path('<int:role_id>/edit/', edit_role, name='edit'),
    path('<int:role_id>/', RoleDetailView.as_view(), name='detail'),
    path('by-idea/<int:idea_id>/', RolesListView.as_view(), name='role_list'),
    path('<int:role_id>/delete/', DeleteRoleView.as_view(), name='delete_role'),
]
