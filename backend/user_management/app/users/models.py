from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils.translation import gettext_lazy as _
from PIL import Image

# Create your models here.

class User(AbstractUser):
    username = models.CharField(max_length=100, unique=True)
    password = models.CharField(max_length=100, min_length=8)
    email = models.EmailField(_('email address'), max_length=100, unique=True)
    image = models.ImageField(upload_to='profile_pics/', default='default_pp.jpg')

    REQUIRED_FIELDS = []


class Friendship(models.Model):
    sender = models.ForeignKey(User, on_delete=models.CASCADE, related_name='sent_friend_request')
    receiver = models.ForeignKey(User, on_delete=models.CASCADE, related_name='received_friend_request')
    status_choices = [
        ('pending', 'Pending'),
        ('accepted', 'Accepted'),
        ('declined', 'Declined'),
    ]
    status = models.CharField(max_length=10, choices=status_choices)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ['sender', 'receiver']
