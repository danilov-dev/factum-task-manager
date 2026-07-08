from django.contrib.auth.decorators import login_required
from django.http import HttpResponseNotAllowed, HttpResponseBadRequest
from django.shortcuts import get_object_or_404, render

from apps.ideas.models import Idea
from apps.likes.services import switch
from apps.posts.models import Post


@login_required
def switch_like(request, content_type, object_id):
    if request.method != 'POST':
        return HttpResponseNotAllowed(['POST'])

    model_map = {
        'idea': Idea,
        'post': Post,
    }

    model = model_map.get(content_type)
    if not model:
        return HttpResponseBadRequest('Invalid content type')

    obj = get_object_or_404(model, pk=object_id)
    is_liked, likes_count = switch(request.user, obj)

    return render(request, 'likes/partials/like_button.html', {
        'content_type': content_type,
        'object_id': object_id,
        'obj': obj,
        'likes_count': likes_count,
        'is_liked': is_liked,
    })