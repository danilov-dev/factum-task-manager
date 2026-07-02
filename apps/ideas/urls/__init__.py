from django.urls import path, include

app_name = 'ideas'

urlpatterns = [
    path('', include('apps.ideas.urls.idea')),
    path('roles/', include('apps.ideas.urls.role')),
    path('responses/', include('apps.ideas.urls.response')),
]