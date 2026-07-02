from django.urls import path
from ..views import response

app_name = 'responses'

urlpatterns = [
    path('create/<int:role_id>/', response.create_response_view, name='create'),
    path('my/', response.my_responses, name='my_responses'),
    path('idea/<int:idea_id>/', response.idea_responses, name='idea_responses'),
    path('<int:response_id>/approve/', response.approve_response_view, name='approve'),
    path('<int:response_id>/reject/', response.reject_response_view, name='reject'),
]