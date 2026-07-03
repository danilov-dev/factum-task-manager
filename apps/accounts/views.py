import logging

from django.contrib import messages
from django.contrib.auth import logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.views import LoginView
from django.shortcuts import redirect, render
from django.urls import reverse_lazy
from django.views.decorators.http import require_http_methods
from django.views.generic import CreateView

from apps.accounts.forms import CustomUserCreationForm, CustomAuthenticationForm

logger = logging.getLogger(__name__)

class UserRegisterView(CreateView):
    """Представление для регистрации."""
    form_class = CustomUserCreationForm
    success_url = reverse_lazy('home')
    template_name = 'accounts/register.html'

    def form_valid(self, form):
        response = super().form_valid(form)
        logger.info("Зарегистрирован новый пользователь: %s", self.object.username)
        return response

class UserLoginView(LoginView):
    """Представление для входа."""
    form_class = CustomAuthenticationForm
    template_name = 'accounts/login.html'

    def form_valid(self, form):
        user = form.get_user()
        logger.info("Успешный вход пользователя: %s", user.username)
        messages.success(self.request, f'С возвращением, {user.username}!')
        return super().form_valid(form)

@require_http_methods(["POST", "GET"])
@login_required
def logout_view(request):
    """Кастомный выход из системы"""
    if request.method == 'POST':
        username = request.user.username
        logout(request)
        logger.info("Пользователь вышел из системы: %s", username)
        messages.success(request, 'Вы успешно вышли из системы.')
        return redirect('accounts:login')
    else:
        return render(request, 'accounts/logout_confirm.html')
