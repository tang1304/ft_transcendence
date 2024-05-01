from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.shortcuts import render
from .serializer import RegisterSerializer, LoginSerializer


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
