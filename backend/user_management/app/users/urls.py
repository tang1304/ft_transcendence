from django.urls import path
from .views import (RegisterView, LoginView, LogoutView, SendFriendRequestView, AcceptFriendRequestView, UpdateUserView,
                    DeleteFriendView, ListFriendsView, Enable2FAView, Disable2FAView)#, DeclineFriendRequestView)

urlpatterns = [
    path('register', RegisterView.as_view()),
    path('login', LoginView.as_view()),
    path('logout', LogoutView.as_view()),
    path('user', UpdateUserView.as_view()),
    path('send_friend', SendFriendRequestView.as_view()),
    path('accept_friend', AcceptFriendRequestView.as_view()),
    path('delete_friend', DeleteFriendView.as_view()),
    path('list_friends', ListFriendsView.as_view()),
    path('enable_2FA', Enable2FAView.as_view()),
    path('disable_2FA', Disable2FAView.as_view()),
    # path('decline_friend', DeclineFriendRequestView.as_view()),
]
