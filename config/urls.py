from django.contrib import admin
from django.urls import path, include
from django.views.generic import TemplateView

urlpatterns = [
    path('admin/', admin.site.urls),
    path('markdownx/', include('markdownx.urls')),
    path('accounts/', include('apps.accounts.urls', namespace='accounts')),
    path('users/', include('apps.users.urls', namespace='users')),
    path('ideas/', include('apps.ideas.urls', namespace='ideas')),
    path('subscriptions/', include('apps.subscriptions.urls'), name='subscriptions'),
    path('', TemplateView.as_view(template_name='index.html'), name='home'),
    path('__debug__/', include('debug_toolbar.urls')),
]

from django.conf import settings
from django.conf.urls.static import static

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
