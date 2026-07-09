import logging

from django.contrib.auth.decorators import login_required
from django.http import HttpResponseNotAllowed, HttpResponseBadRequest
from django.shortcuts import get_object_or_404, render

from apps.ideas.models import Idea
from apps.likes.services import switch, is_liked
from apps.posts.models import Post

logger = logging.getLogger(__name__)

@login_required
def switch_like(request, content_type, object_id):
    if request.method != 'POST':
        return HttpResponseNotAllowed(['POST'])

    try:
        value = int(request.POST.get('value', 1))
        if value not in [1, -1]:
            logger.error(f'Invalid value {value} in {content_type}:{object_id}')
            return HttpResponseBadRequest('Invalid value')
    except (ValueError, TypeError):
        logger.error(f'Invalid request for like in {content_type}:{object_id}')
        return HttpResponseBadRequest('Invalid value')

    model_map = {
        'idea': Idea,
        'post': Post,
    }
    model = model_map.get(content_type)

    if not model:
        logger.error(f'Invalid content type {content_type}:{object_id}')
        return HttpResponseBadRequest('Invalid content type')

    obj = get_object_or_404(model, pk=object_id)
    print(value)
    new_value, likes_count, dislikes_count = switch(user=request.user, obj=obj, value=value)

    score = likes_count - dislikes_count

    return render(request, 'likes/partials/like_button.html', {
        'content_type': content_type,
        'object_id': object_id,
        'obj': obj,
        'likes_count': likes_count,
        'dislikes_count': dislikes_count,
        'user_reaction': new_value,
        'score': score,
    })
