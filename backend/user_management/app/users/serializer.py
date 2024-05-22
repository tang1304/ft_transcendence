from .models import User
from .utils import send_email
from rest_framework import serializers
from django.contrib.auth import authenticate
from django.contrib.auth.tokens import PasswordResetTokenGenerator
from django.contrib.sites.shortcuts import get_current_site
from django.utils.encoding import smart_str, force_str, smart_bytes, DjangoUnicodeDecodeError
from django.utils.http import urlsafe_base64_decode, urlsafe_base64_encode
from django.urls import reverse
from rest_framework.exceptions import AuthenticationFailed
import jwt
import pyotp
import os
from datetime import datetime, timedelta, timezone
from django.contrib.auth.hashers import check_password
from django.contrib.auth.password_validation import validate_password

class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(max_length=100, min_length=8, write_only=True)
    password2 = serializers.CharField(max_length=100, min_length=8, write_only=True)

    class Meta:
        model = User
        fields = ['email', 'first_name', 'last_name', 'username', 'password', 'password2']

    def validate(self, attrs):
        password = attrs.get('password', '')
        password2 = attrs.get('password2', '')
        if password != password2:
            raise serializers.ValidationError("passwords don't match")
        return attrs

    def create(self, validated_data):
        user = User.objects.create_user(
            email=validated_data['email'],
            first_name=validated_data.get('first_name'),
            last_name=validated_data.get('last_name'),
            username=validated_data.get('username'),
            password=validated_data.get('password'),
        )
        return user


class LoginSerializer(serializers.ModelSerializer):
    username = serializers.CharField(max_length=100)
    password = serializers.CharField(max_length=50, write_only=True)

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

        if user.tfa_activated:
            return {'user': user}

        payload = {
            'id': user.id,
            'exp': datetime.now(timezone.utc) + timedelta(hours=1),  # time before expiration
            'iat': datetime.now(timezone.utc),  # Issued AT
        }
        secret = os.environ.get('SECRET_KEY')
        token = jwt.encode(payload, secret, algorithm='HS256')

        return {
            'user': user,
            'token': token
        }


class UserSerializer(serializers.ModelSerializer):
    image = serializers.ImageField(max_length=255, allow_empty_file=False, use_url=True)

    class Meta:
        model = User
        fields = ['username', 'first_name', 'last_name', 'image']


class PasswordChangeSerializer(serializers.Serializer):
    old_password = serializers.CharField(max_length=100, min_length=8, write_only=True)
    new_password = serializers.CharField(max_length=100, min_length=8, write_only=True)
    confirm_password = serializers.CharField(max_length=100, min_length=8, write_only=True)

    def validate(self, attrs):
        user = self.context['user']
        old_password = attrs.get('old_password')
        new_password = attrs.get('new_password')
        confirm_password = attrs.get('confirm_password')

        if not user.check_password(old_password):
            raise serializers.ValidationError("Old password is incorrect")
        if new_password != confirm_password:
            raise serializers.ValidationError("New passwords do not match")

        validate_password(new_password, user)
        return attrs

    def save(self, **kwargs):
        user = self.context['user']
        new_password = self.validated_data['new_password']
        user.set_password(new_password)
        user.save()


class PasswordResetRequestSerializer(serializers.Serializer):
    email = serializers.EmailField(max_length=100)

    class Meta:
        model = User
        fields = ['email']

    def validate(self, attrs):
        email = attrs.get('email')
        if User.objects.filter(email=email).exists():
            user = User.objects.get(email=attrs.get('email'))
            uidb64 = urlsafe_base64_encode(smart_bytes(user.id))
            token = PasswordResetTokenGenerator().make_token(user)
            request = self.context.get('request')
            relative_link = reverse('reset-confirmed', kwargs={'uidb64': uidb64, 'token': token})
            current_site = get_current_site(request).domain
            abslink = f"http://{current_site}{relative_link}"
            content = f"Hello {user.username}, use this link to reset your password: {abslink}"
            data = {
                'email_body': content,
                'to_email': user.email,
                'email_subject': 'Password reset request',
            }
            send_email(data)
        else:
            raise serializers.ValidationError("No user with that email exists")

        return super().validate(attrs)


#TODO: NEEDS TESTS WITH FRONTEND TO CHECK TOKEN AND UIDB64
class SetNewPasswordSerializer(serializers.Serializer):
    uidb64 = serializers.CharField(write_only=True, required=True)
    token = serializers.CharField(write_only=True, required=True)
    new_password = serializers.CharField(write_only=True, required=True, max_length=100, min_length=8)
    confirm_password = serializers.CharField(write_only=True, required=True, max_length=100, min_length=8)

    def validate(self, attrs):
        try:
            user_id = smart_str(urlsafe_base64_decode(attrs['uidb64']))
            user = User.objects.get(id=user_id)

            if not PasswordResetTokenGenerator().check_token(user, attrs['token']):
                raise serializers.ValidationError({'detail': "Invalid or expired token"})

            new_password = attrs.get('new_password')
            confirm_password = attrs.get('confirm_password')
            if new_password != confirm_password:
                raise serializers.ValidationError("New passwords do not match")
            user.set_password(attrs['password'])
            user.save()

        except DjangoUnicodeDecodeError:
            raise serializers.ValidationError({'detail': "Invalid token"})


class VerifyOTPSerializer(serializers.ModelSerializer):
    user_id = serializers.IntegerField()
    otp = serializers.CharField(max_length=6, write_only=True)

    class Meta:
        model = User
        fields = ['user_id', 'otp']

    def validate(self, attrs):
        user_id = attrs.get('user_id')
        otp = attrs.get('otp')

        try:
            user = User.objects.get(id=user_id)
        except User.DoesNotExist:
            raise AuthenticationFailed("User not found")

        if not user.tfa_activated:
            raise AuthenticationFailed("2FA not enabled for this user")

        totp = pyotp.TOTP(user.totp)
        if not totp.verify(otp):
            raise AuthenticationFailed("Invalid OTP")

        payload = {
            'id': user.id,
            'exp': datetime.now(timezone.utc) + timedelta(hours=1),  # time before expiration
            'iat': datetime.now(timezone.utc),  # Issued AT
        }
        secret = os.environ.get('SECRET_KEY')
        token = jwt.encode(payload, secret, algorithm='HS256')

        return {
            'user': user,
            'token': token
        }
