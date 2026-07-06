from django.contrib.auth.decorators import login_required
from django.http import HttpResponseForbidden
from django.shortcuts import render, get_object_or_404

from apps.ideas.models import Idea
from apps.subscriptions.services import switch


@login_required
def switch_subscription(request, idea_id):
    idea = get_object_or_404(Idea, id=idea_id)

    if request.method != 'POST':
        return HttpResponseForbidden('Только post')

    is_now_subscribed = switch(request.user, idea)

    return render(request, 'subscriptions/partials/_subscribe_button.html', {
        'idea': idea,
        'is_subscribed': is_now_subscribed,
    })

