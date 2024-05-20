import jwt
from django.middleware.csrf import get_token
from django.views.decorators.csrf import csrf_protect
from django.utils.decorators import method_decorator
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.exceptions import AuthenticationFailed
from rest_framework import status
from .serializer import (RegisterSerializer, LoginSerializer, UserSerializer, VerifyOTPSerializer, PasswordResetSerializer)
from .models import User, FriendRequest
import os
import pyotp
import logging  # for debug


def authenticate_user(request):
    token = request.COOKIES.get('jwt')
    if not token:
        raise AuthenticationFailed('Unauthenticated')

    secret = os.environ.get('SECRET_KEY')
    payload = jwt.decode(token, secret, algorithms=['HS256'])
    user_id = payload.get('id')

    try:
        user = User.objects.get(id=user_id)
    except User.DoesNotExist:
        raise AuthenticationFailed('User not found')

    return user

@method_decorator(csrf_protect, name='dispatch')
class RegisterView(APIView):
    serializer_class = RegisterSerializer
    def post(self, request):
        user_data = request.data
        serializer = self.serializer_class(data=user_data)
        if serializer.is_valid(raise_exception=True):
            serializer.save()
            user = serializer.data
            return Response({
                'data': user,
                'message': f'Signing up done'
            }, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@method_decorator(csrf_protect, name='dispatch')
class LoginView(APIView):
    serializer_class = LoginSerializer
    def post (self, request):
        serializer = self.serializer_class(data=request.data, context={'request': request})
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data['user']

        if user.tfa_activated:
            return Response({
                'detail': 'OTP required for your account',
                'otp_required': True,
                'user_id': user.id
            })

        token = serializer.validated_data['token']
        user.status = 'online'
        user.save()

        response = Response({"token": token})
        response.set_cookie(key='jwt', value=token, httponly=True)
        response.set_cookie(key='csrftoken', value=get_token(request), samesite='Lax', secure=True)
        return response


@method_decorator(csrf_protect, name='dispatch')
class LogoutView(APIView):
    def post(self, request):
        user = authenticate_user(request)

        user.status = 'offline'
        user.save()

        response = Response({"detail": "Logged out successfully"})
        response.delete_cookie('jwt')
        return response


@method_decorator(csrf_protect, name='dispatch')
class UpdateUserView(APIView):
    serializer_class = UserSerializer
    def put(self, request):
        user = authenticate_user(request)

        serializer = self.serializer_class(user, data=request.data, partial=True)
        if serializer.is_valid(raise_exception=True):
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_403_FORBIDDEN)


@method_decorator(csrf_protect, name='dispatch')
class PasswordResetView(APIView):
    serializer_class = PasswordResetSerializer
    def post(self, request):
        user = authenticate_user(request)
        serializer = self.serializer_class(data=request.data, context={'user': user})
        if serializer.is_valid(raise_exception=True):
            serializer.save()
            return Response({"detail": "Password changed successfully"})
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@method_decorator(csrf_protect, name='dispatch')
class Enable2FAView(APIView):
    def post(self, request):
        user = authenticate_user(request)

        if user.tfa_activated is True:
            return Response({"detail": "2FA already activated"}, status=status.HTTP_400_BAD_REQUEST)
        secret_key = pyotp.random_base32()
        user.totp = secret_key
        user.tfa_activated = True
        user.save()

        qr_url = pyotp.totp.TOTP(secret_key).provisioning_uri(user.username)
        response = Response({"qr_url": qr_url}, status=status.HTTP_200_OK)
        return response


@method_decorator(csrf_protect, name='dispatch')
class VerifyOTPView(APIView):
    def post(self, request):
        serializer = VerifyOTPSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        token = serializer.validated_data['token']
        user = serializer.validated_data['user']

        user.status = 'online'
        user.save()

        response = Response({"token": token})
        response.set_cookie(key='jwt', value=token, httponly=True)
        return response


@method_decorator(csrf_protect, name='dispatch')
class Disable2FAView(APIView):
    def post(self, request):
        user = authenticate_user(request)

        if user.tfa_activated is False:
            return Response({"detail": "2FA already deactivated"}, status=status.HTTP_400_BAD_REQUEST)
        user.totp = None
        user.tfa_activated = False
        user.save()
        return Response({"detail": "2FA disabled"}, status=status.HTTP_200_OK)


@method_decorator(csrf_protect, name='dispatch')
class SendFriendRequestView(APIView):
    def post(self, request):
        user = authenticate_user(request)
        to_user_id = request.data.get('to_id')

        try:
            to_user = User.objects.get(pk=to_user_id)
        except User.DoesNotExist:
            return Response({'detail': 'User does not exist.'}, status=status.HTTP_404_NOT_FOUND)

        if user == to_user:
            return Response({'detail': 'You cannot send a friend request to yourself.'},
                            status=status.HTTP_400_BAD_REQUEST)

        if user.friends.filter(id=to_user_id).exists():
            return Response({'detail': 'This user is already your friend.'}, status=status.HTTP_400_BAD_REQUEST)

        if FriendRequest.objects.filter(from_user=user, to_user=to_user).exists():
            return Response({'detail': 'Friend request already sent.'}, status=status.HTTP_400_BAD_REQUEST)

        if FriendRequest.objects.filter(from_user=to_user, to_user=user, status='pending').exists():
            return Response({'detail': 'You have a pending request from this user.'},
                            status=status.HTTP_400_BAD_REQUEST)

        FriendRequest.objects.create(from_user=user, to_user=to_user)
        return Response({'detail': 'Friend request sent.'}, status=status.HTTP_201_CREATED)


@method_decorator(csrf_protect, name='dispatch')
class AcceptFriendRequestView(APIView):
    def post(self, request):
        user = authenticate_user(request)
        friend_request_user_id = request.data.get('from_id')
        try:
            friend_request = FriendRequest.objects.get(from_user_id=friend_request_user_id, to_user_id=user)
        except FriendRequest.DoesNotExist:
            return Response({'detail': 'Friend request does not exist.'}, status=status.HTTP_404_NOT_FOUND)

        if friend_request.to_user != user:
            return Response({'detail': 'You cannot accept this friend request.'}, status=status.HTTP_403_FORBIDDEN)

        if FriendRequest.objects.filter(from_user_id=friend_request_user_id, to_user_id=user,
                                        status='accepted').exists():
            return Response({'detail': 'You already accepted this friend request.'}, status=status.HTTP_403_FORBIDDEN)

        friend_request.status = 'accepted'
        friend_request.save()

        friend_request.to_user.friends.add(friend_request.from_user)
        friend_request.from_user.friends.add(friend_request.to_user)

        return Response({'detail': 'Friend request accepted.'}, status=status.HTTP_200_OK)

# TODO: If necessary, otherwise we stay with pending requests
# class DeclineFriendRequestView(APIView):
#     def post(self, request):
#         token = request.COOKIES.get('jwt')
#         if not token:
#             raise AuthenticationFailed('Unauthenticated')
#         friend_request_id = request.data.get('friend_request_id')
#         try:
#             friend_request = FriendRequest.objects.get(pk=friend_request_id)
#         except FriendRequest.DoesNotExist:
#             return Response({'detail': 'Friend request does not exist.'}, status=status.HTTP_404_NOT_FOUND)
#
#         if friend_request.to_user != request.user:
#             return Response({'detail': 'You cannot decline this friend request.'}, status=status.HTTP_403_FORBIDDEN)
#
#         friend_request.delete()
#
#         return Response({'detail': 'Friend request declined.'}, status=status.HTTP_200_OK)


@method_decorator(csrf_protect, name='dispatch')
class DeleteFriendView(APIView):
    def post(self, request):
        user = authenticate_user(request)
        friend_id = request.data.get('to_id')
        try:
            friend = User.objects.get(id=friend_id)
        except User.DoesNotExist:
            return Response({'detail': 'Friend does not exist.'}, status=status.HTTP_404_NOT_FOUND)

        if friend in user.friends.all():
            user.friends.remove(friend)
            friend.friends.remove(user)

            try:
                friend_request = FriendRequest.objects.get(from_user_id=friend_id, to_user_id=user)
                friend_request.delete()
            except FriendRequest.DoesNotExist:
                pass
            try:
                friend_request = FriendRequest.objects.get(from_user_id=user, to_user_id=friend_id)
                friend_request.delete()
            except FriendRequest.DoesNotExist:
                pass

            return Response({'detail': 'Friend removed.'}, status=status.HTTP_200_OK)

        return Response({'detail': 'User is not in your friends.'}, status=status.HTTP_400_BAD_REQUEST)


@method_decorator(csrf_protect, name='dispatch')
class ListFriendsView(APIView):
    def post(self, request):
        user = authenticate_user(request)
        friends = user.friends.all()
        friends_data = []
        if friends:
            for friend in friends:
                friends_data.append({
                    'username': friend.username,
                    'status': friend.status,
                })
            return Response(friends_data, status=status.HTTP_200_OK)
        else:
            return Response({'detail': 'No friends yet.'}, status=status.HTTP_200_OK)
