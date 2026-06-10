from django.urls import path

from apps.users.views import ProfileView, UsersListView

app_name = 'users'

urlpatterns = [
    path('<str:username>/', ProfileView.as_view(), name='profile'),
    path('', UsersListView.as_view(), name='user_list'),
]
