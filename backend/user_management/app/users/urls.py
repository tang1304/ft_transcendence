from django.urls import path
from .views import (RegisterView, LoginView, LogoutView, SendFriendRequestView, AcceptFriendRequestView, UpdateUserView,
                    DeleteFriendView, ListFriendsView, Enable2FAView, Disable2FAView, VerifyOTPView, PasswordChangeView
                    , PasswordResetRequestView, PasswordResetConfirmedView)#, DeclineFriendRequestView)

urlpatterns = [
    path('register', RegisterView.as_view()),
    path('login', LoginView.as_view()),
    path('logout', LogoutView.as_view()),
    path('user', UpdateUserView.as_view()),
    path('change_password', PasswordChangeView.as_view()),
    path('reset_password', PasswordResetRequestView.as_view()),
    path('reset_password_confirmed/<uidb64>/<token>/', PasswordResetConfirmedView.as_view(), name='reset-confirmed'),
    path('send_friend', SendFriendRequestView.as_view()),
    path('accept_friend', AcceptFriendRequestView.as_view()),
    path('delete_friend', DeleteFriendView.as_view()),
    path('list_friends', ListFriendsView.as_view()),
    path('enable_2FA', Enable2FAView.as_view()),
    path('verifyotp', VerifyOTPView.as_view()),
    path('disable_2FA', Disable2FAView.as_view()),
    # path('decline_friend', DeclineFriendRequestView.as_view()),
]
