from django.contrib import admin
from django.urls import path, include
from django.views.generic import TemplateView

urlpatterns = [
    path('admin/', admin.site.urls),
    path('accounts/', include('apps.accounts.urls', namespace='accounts')),
    path('users/', include('apps.users.urls', namespace='users')),
    path('', TemplateView.as_view(template_name='index.html'), name='home'),
]
