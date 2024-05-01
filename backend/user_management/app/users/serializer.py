from .models import User
from rest_framework import serializers
from django.contrib.auth import authenticate
from rest_framework.exceptions import AuthenticationFailed
import jwt
import os
from datetime import datetime, timedelta, timezone


class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(max_length=30, min_length=8, write_only=True)
    password2 = serializers.CharField(max_length=30, min_length=8, write_only=True)

    class Meta:
        model = User
        fields = ['email', 'username', 'password', 'password2']

    def validate(self, attrs):
        password = attrs.get('password', '')
        password2 = attrs.get('password2', '')
        if password != password2:
            raise serializers.ValidationError("passwords don't match")
        return attrs

    def create(self, validated_data):
        user = User.objects.create_user(
            email=validated_data['email'],
            username=validated_data.get('username'),
            password=validated_data.get('password')
        )
        return user


class LoginSerializer(serializers.ModelSerializer):
    username = serializers.CharField(max_length=100)
    password = serializers.CharField(max_length=30, write_only=True)

    class Meta:
        model = User
        fields = ['username', 'password']
        extra_kwargs = {
            'password': {'write_only': True}
        }

    def validate(self, attrs):
        username = attrs.get('username')
        password = attrs.get('password')
        request = self.context.get('request')

        user = authenticate(request, username=username, password=password)
        if not user:
            raise AuthenticationFailed("Invalid, please try again")

        payload = {
            'id': user.id,
            'exp': datetime.now(timezone.utc) + timedelta(hours=1),  # time before expiration
            'iat': datetime.now(timezone.utc),  # Issued AT
        }
        secret = os.environ.get('SECRET_KEY')
        token = jwt.encode(payload, secret, algorithm='HS256')

        return {
            'token': token
        }
