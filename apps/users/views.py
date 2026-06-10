from django.shortcuts import render, get_object_or_404
from django.views import View
from django.views.generic import ListView
from apps.users.models import User


class ProfileView(View):
    """Представление профиля пользователя"""
    model = User
    template_name = 'users/profile.html'
    context_object_name = 'profile_user'

    def get_object(self, queryset=None):
        username = self.kwargs.get('username')
        if username:
            return get_object_or_404(User, username=username)
        return self.request.user

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.get_object()
        context['is_owen_profile'] = user == self.request.user
        return context

class UsersListView(ListView):
    """Представление списка пользователя"""
    model = User
    template_name = 'users/users.html'
    context_object_name = 'users'
    paginate_by = 5

    def get_queryset(self):
        return User.objects.all()







