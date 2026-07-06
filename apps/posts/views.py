import logging

from django.contrib import messages
from django.shortcuts import get_object_or_404
from django.urls import reverse_lazy
from django.views.generic import CreateView, DetailView

from apps.posts.forms import PostCreateForm
from apps.posts.models import Post

logger = logging.getLogger(__name__)


class PostDetailView(DetailView):
    model = Post
    template_name = 'posts/detail.html'
    context_object_name = 'post'

    def get_object(self, queryset=None):
        post = get_object_or_404(Post, pk=self.kwargs['pk'])
        return post


class CreatePost(CreateView):
    model = Post
    form_class = PostCreateForm
    template_name = 'posts/create_post.html'

    def form_valid(self, form):
        post = Post.objects.create(author=self.request.user, **form.cleaned_data)

        logger.debug('Post "%s" (id=%d) created by user %s', post.title, post.pk, self.request.user)
        messages.success(self.request, f'Пост {post.title} опубликован')

        return super().form_valid(form)

    def get_success_url(self):
        return reverse_lazy('posts:detail', kwargs={'pk': self.object.pk})
