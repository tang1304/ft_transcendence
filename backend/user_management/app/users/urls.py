from django.urls import path
from .views import RegisterView, LoginView, LogoutView, SendFriendRequestView, AcceptFriendRequestView, UpdateUserView#, DeclineFriendRequestView)

urlpatterns = [
    path('register', RegisterView.as_view()),
    path('login', LoginView.as_view()),
    path('logout', LogoutView.as_view()),
    path('send_friend', SendFriendRequestView.as_view()),
    path('accept_friend', AcceptFriendRequestView.as_view()),
    path('user', UpdateUserView.as_view()),
    # path('decline_friend', DeclineFriendRequestView.as_view()),
]
