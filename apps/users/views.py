from django.shortcuts import render, get_object_or_404
from django.views import View
from django.views.generic import ListView, DetailView

from apps.ideas.services import get_user_ideas
from apps.users.models import User


class ProfileView(DetailView):
    """Представление профиля пользователя"""
    model = User
    template_name = 'users/profile.html'
    context_object_name = 'profile_user'
    slug_field = 'username'
    slug_url_kwarg = 'username'

    def get_object(self, queryset=None):
        username = self.kwargs.get('username')
        if username:
            return get_object_or_404(User, username=username)
        return self.request.user

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.object
        is_own = user == self.request.user
        context['is_own_profile'] = is_own
        context['ideas'] = get_user_ideas(user, viewer=self.request.user)
        return context

class UsersListView(ListView):
    """Представление списка пользователя"""
    model = User
    template_name = 'users/users.html'
    context_object_name = 'users'
    paginate_by = 5

    def get_queryset(self):
        return User.objects.all()







