from django.urls import path, include

from apps.ideas.urls import idea, role, response

app_name = 'ideas'

urlpatterns = [
    path('', include(idea)),
    path('<int:idea_id>/posts/', include('apps.posts.urls', namespace='posts')),
    path('<int:idea_id>/roles/', include(role, namespace='roles')),
    path('<int:idea_id>/responses/', include(response, namespace='responses')),
]