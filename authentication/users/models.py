from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils.translation import gettext_lazy as _


# Create your models here.

class User(AbstractUser):
    username = models.CharField(max_length=255, unique=True)
    password = models.CharField(max_length=255)
    email = models.CharField(max_length=255, unique=True)

    REQUIRED_FIELDS = []


class Friendship(models.Model):
    sender = models.ForeignKey(User, on_delete=models.CASCADE, related_name='sent_friend_request')
    receiver = models.ForeignKey(User, on_delete=models.CASCADE, related_name='received_friend_request')
    status_choices = [
        ('pending', 'Pending'),
        ('accepted', 'Accepted'),
        ('declined', 'Declined'),
    ]
    status = models.CharField(max_length=10, choices=status_choices, default="pending")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ['sender', 'receiver']
