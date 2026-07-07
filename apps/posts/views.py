import logging

from django.contrib import messages
from django.shortcuts import get_object_or_404
from django.urls import reverse_lazy
from django.views.generic import CreateView, DetailView, ListView

from apps.ideas.models import Idea
from apps.posts.forms import PostCreateForm
from apps.posts.models import Post, PostQuerySet

logger = logging.getLogger(__name__)


class PostDetailView(DetailView):
    model = Post
    template_name = 'posts/detail.html'
    context_object_name = 'post'

    def get_object(self, queryset=None):
        post = get_object_or_404(Post, pk=self.kwargs['post_id'])
        return post

class PostListView(ListView):
    model = Post
    template_name = 'posts/list.html'
    context_object_name = 'posts'

    def get_queryset(self):
        idea_id = self.kwargs.get('idea_id')
        return Post.objects.for_idea(idea_id=idea_id)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        posts = context['posts']

        if posts.exists():
            idea = posts[0].idea
        else:
            idea = get_object_or_404(Idea, pk=self.kwargs['idea_id'])

        context['idea_id'] = self.kwargs['idea_id']
        context['idea_title'] = idea.title
        return context

class CreatePost(CreateView):
    model = Post
    form_class = PostCreateForm
    template_name = 'posts/create.html'

    def dispatch(self, request, *args, **kwargs):
        self.idea = get_object_or_404(Idea, pk=kwargs['idea_id'])
        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['idea'] = self.idea
        return context

    def form_valid(self, form):
        post = form.save(commit=False)
        post.idea = self.idea
        post.author = self.request.user
        post.save()

        logger.debug('Post "%s" (id=%d) created by user %s for idea %s',
                    post.title, post.pk, self.request.user, self.idea.title)
        messages.success(self.request, f'Пост "{post.title}" опубликован для идеи "{self.idea.title}"')

        return super().form_valid(form)

    def get_success_url(self):
        return reverse_lazy('ideas:posts:detail', kwargs={'idea_id': self.idea.pk,'post_id': self.object.pk})
