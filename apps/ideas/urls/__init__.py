from django.urls import path, include

app_name = 'ideas'

urlpatterns = [
    path('', include('apps.ideas.urls.idea_urls')),
    path('roles/', include('apps.ideas.urls.role_urls')),
]