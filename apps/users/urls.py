from django.urls import path

from apps.users.views import ProfileView, UsersListView, user_menu

app_name = 'users'

urlpatterns = [
    path('menu/', user_menu, name='menu'),
    path('<str:username>/', ProfileView.as_view(), name='profile'),
    path('', UsersListView.as_view(), name='user_list'),
]
