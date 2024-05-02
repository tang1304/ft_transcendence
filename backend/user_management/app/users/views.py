import jwt
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.exceptions import AuthenticationFailed
from rest_framework import status
from django.shortcuts import render
from .serializer import RegisterSerializer, LoginSerializer, LogoutSerializer#, PasswordResetSerializer
from .models import User, FriendRequest
import os
import logging  # for debug
# Create your views here.

class RegisterView(APIView):
    serializer_class = RegisterSerializer
    def post(self, request):
        user_data = request.data
        serializer = self.serializer_class(data=user_data)
        if serializer.is_valid(raise_exception=True):
            serializer.save()
            user = serializer.data
            #2fa
            return Response({
                'data': user,
                'message': f'Signing up done, check your emails to verify your account'
            }, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class LoginView(APIView):
    serializer_class = LoginSerializer

    def post (self, request):
        serializer = self.serializer_class(data=request.data, context={'request': request})
        serializer.is_valid(raise_exception=True)
        token = serializer.validated_data['token']
        response = Response({"token": token})
        response.set_cookie(key='jwt', value=token, httponly=True)
        return response


class LogoutView(APIView):
    serializer_class = LogoutSerializer
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(status=status.HTTP_204_NO_CONTENT)


# class PasswordResetView(APIView):
#     serializer_class = PasswordResetSerializer
#     def post(self, request):
#         serializer = self.serializer_class(data=request.data, context={'request': request})
#         serializer.is_valid(raise_exception=True)

class SendFriendRequestView(APIView):
    def post(self, request):
        token = request.COOKIES.get('jwt')
        if not token:
            raise AuthenticationFailed('Unauthenticated')
        secret = os.environ.get('SECRET_KEY')
        payload = jwt.decode(token, secret, algorithms='HS256')

        from_user = User.objects.get(id=payload.get('id'))
        to_user_id = request.data.get('to_user_id')

        try:
            to_user = User.objects.get(pk=to_user_id)
        except User.DoesNotExist:
            return Response({'detail': 'User does not exist.'}, status=status.HTTP_404_NOT_FOUND)

        if FriendRequest.objects.filter(from_user=from_user, to_user=to_user).exists():
            return Response({'detail': 'Friend request already sent.'}, status=status.HTTP_400_BAD_REQUEST)

        if from_user == to_user:
            return Response({'detail': 'You cannot send a friend request to yourself.'},
                            status=status.HTTP_400_BAD_REQUEST)

        FriendRequest.objects.create(from_user=from_user, to_user=to_user)
        return Response({'detail': 'Friend request sent.'}, status=status.HTTP_201_CREATED)


class AcceptFriendRequestView(APIView):
    def post(self, request):
        token = request.COOKIES.get('jwt')
        if not token:
            raise AuthenticationFailed('Unauthenticated')
        friend_request_id = request.data.get('friend_request_id')
        friend_request = FriendRequest.objects.get(pk=friend_request_id)

        if friend_request.to_user != request.user:
            return Response({'detail': 'You cannot accept this friend request.'}, status=status.HTTP_403_FORBIDDEN)

        friend_request.accepted = True
        friend_request.save()

        friend_request.from_user.friends.add(request.user)
        request.user.friends.add(friend_request.from_user)

        return Response({'detail': 'Friend request accepted.'}, status=status.HTTP_200_OK)


class DeclineFriendRequestView(APIView):
    def post(self, request):
        token = request.COOKIES.get('jwt')
        if not token:
            raise AuthenticationFailed('Unauthenticated')
        friend_request_id = request.data.get('friend_request_id')
        try:
            friend_request = FriendRequest.objects.get(pk=friend_request_id)
        except FriendRequest.DoesNotExist:
            return Response({'detail': 'Friend request does not exist.'}, status=status.HTTP_404_NOT_FOUND)

        if friend_request.to_user != request.user:
            return Response({'detail': 'You cannot decline this friend request.'}, status=status.HTTP_403_FORBIDDEN)

        friend_request.delete()

        return Response({'detail': 'Friend request declined.'}, status=status.HTTP_200_OK)
