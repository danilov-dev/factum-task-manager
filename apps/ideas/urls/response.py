from django.urls import path

from apps.ideas.views.response import (
    ResponseCreateView,
    MyResponsesListView,
    IdeaResponsesListView,
    approve_response_view,
    reject_response_view,
    cancel_response_view,
)

app_name = 'responses'

urlpatterns = [
    path('create/<int:role_id>/', ResponseCreateView.as_view(), name='create'),
    path('my/', MyResponsesListView.as_view(), name='my_responses'),
    path('idea/<int:idea_id>/', IdeaResponsesListView.as_view(), name='idea_responses'),
    path('<int:response_id>/approve/', approve_response_view, name='approve'),
    path('<int:response_id>/reject/', reject_response_view, name='reject'),
    path('<int:response_id>/cancel/', cancel_response_view, name='cancel'),
]