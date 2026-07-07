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
    path('create/', RoleCreateView.as_view(), name='create'),
    path('api/skills-by-category/', get_skills_by_category, name='skills_by_category'),
    path('<int:role_id>/edit/', RoleUpdateView.as_view(), name='edit'),
    path('<int:role_id>/', RoleDetailView.as_view(), name='detail'),
    path('', RolesListView.as_view(), name='role_list'),
    path('<int:role_id>/delete/', DeleteRoleView.as_view(), name='delete_role'),
]