from rest_framework.views import APIView
from rest_framework.views import status
from rest_framework.response import Response
from rest_framework.exceptions import AuthenticationFailed
from .serializer import UserSerializer
from .serializer import FriendSerializer
from .models import User
from .models import Friendship
import jwt
from datetime import datetime, timedelta, timezone
from rest_framework.parsers import MultiPartParser, FormParser
from PIL import Image
from io import BytesIO
from django.core.files.uploadedfile import InMemoryUploadedFile

# Create your views here.


class RegisterView(APIView):
    parser_classes = [MultiPartParser, FormParser]

    def post(self, request):
        serializer = UserSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        profile_picture = request.data.get('profile_picture', None)
        if profile_picture:
            img = Image.open(profile_picture)
            max_width = 300
            max_height = 300
            ratio = img.width / img.height

            if img.width > max_width or img.height > max_height:
                new_width = min(img.width, max_width)
                new_height = int(new_width / ratio)
                img.thumbnail((new_width, new_height))

                img_bytes = BytesIO()
                img.save(img_bytes, format='JPEG')
                resized_img = InMemoryUploadedFile(img_bytes, None, profile_picture.name, 'image/jpeg', None)
                request.data['profile_picture'] = resized_img
        serializer.save()
        return Response(serializer.data)


class LoginView(APIView):
    def post(self, request):
        username = request.data['username']
        password = request.data['password']

        user = User.objects.filter(username=username).first()

        if user is None:
            raise AuthenticationFailed('User not found')

        if not user.check_password(password):
            raise AuthenticationFailed('Incorrect password')

        payload = {
            'id': user.id,
            'exp': datetime.now(timezone.utc) + timedelta(minutes=5),
            'iat': datetime.now(timezone.utc),
        }

        token = jwt.encode(payload, 'secret', algorithm='HS256').decode('utf-8')

        response = Response()

        response.set_cookie(key='jwt', value=token, httponly=True)
        response.data = {
            'jwt': token
        }

        return response


class UserView(APIView):
    def get(self, request):
        token = request.COOKIES.get('jwt')

        if not token:
            raise AuthenticationFailed('Unauthenticated')

        try:
            payload = jwt.decode(token, 'secret', algorithm=['HS256'])
        except jwt.ExpiredSignatureError:
            raise AuthenticationFailed('Unauthenticated')

        user = User.objects.filter(id=payload['id']).first()
        serializer = UserSerializer(user)

        return Response(serializer.data)


class LogoutView(APIView):
    def post(self, request):
        response = Response()
        response.delete_cookie('jwt')
        response.data = {
            'message': 'success'
        }
        return response


class FriendRequestView(APIView):
    def post(self, request):
        token = request.COOKIES.get('jwt')
        if not token:
            raise AuthenticationFailed('Unauthenticated')

        serializer = FriendSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def get(self, request):
        user = request.user
        sent_request = Friendship.objects.filter(sender=user)
        received_request = Friendship.objects.filter(receiver=user)
