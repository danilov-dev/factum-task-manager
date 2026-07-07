from django.urls import path

from apps.posts.views import PostDetailView, CreatePost, PostListView

app_name = 'posts'
urlpatterns = [
    path('create/', CreatePost.as_view(), name='create'),
    path('<int:post_id>/', PostDetailView.as_view(), name='detail'),
    path('', PostListView.as_view(), name='list'),
]
