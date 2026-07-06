from django.urls import path

from apps.ideas.views.role import (
    RoleCreateView,
    RoleUpdateView,
    RoleDetailView,
    RolesListView,
    DeleteRoleView,
    get_skills_by_category,
)

app_name = 'roles'

urlpatterns = [
    path('<int:pk>/create/', RoleCreateView.as_view(), name='create_role'),
    path('api/skills-by-category/', get_skills_by_category, name='skills_by_category'),
    path('<int:role_id>/edit/', RoleUpdateView.as_view(), name='edit'),
    path('<int:role_id>/', RoleDetailView.as_view(), name='detail'),
    path('by-idea/<int:idea_id>/', RolesListView.as_view(), name='role_list'),
    path('<int:role_id>/delete/', DeleteRoleView.as_view(), name='delete_role'),
]