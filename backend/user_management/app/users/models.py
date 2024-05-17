from django.db import models
from django.contrib.auth.models import AbstractUser
from django.core.validators import MinLengthValidator
from rest_framework_simplejwt.tokens import RefreshToken
from .manager import UserManager
from PIL import Image
from .fields import EncryptedField

# Create your models here.

class User(AbstractUser):
    username = models.CharField(unique=True, max_length=100)
    email = models.EmailField(unique=True, max_length=100)
    password = models.CharField(max_length=100, validators=[MinLengthValidator(8)])
    image = models.ImageField(default='default_pp.jpg', upload_to='profile_pics')
    friends = models.ManyToManyField("self", blank=True)
    status_choices = [
        ('online', 'Online'),
        ('offline', 'Offline'),
    ]
    status = models.CharField(max_length=50, choices=status_choices, default='offline')
    totp = EncryptedField(max_length=255, blank=True, null=True)
    tfa_activated = models.BooleanField(default=False)

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        img = Image.open(self.image.path)
        if img.height > 200 or img.width > 200:
            new_img = (200, 200)
            img.thumbnail(new_img)
            img.save(self.image.path)

    REQUIRED_FIELDS = ['email']

    objects = UserManager()

    def __str__(self):
        return self.email

    def get_username(self):
        return self.username

    def token(self):
        refresh = RefreshToken.for_user(self)
        return {
            "refresh": str(refresh),
            "access": str(refresh.access_token)
        }


class FriendRequest(models.Model):
    from_user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='from_user')
    to_user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='to_user')
    status_choices = [
        ('pending', 'Pending'),
        ('accepted', 'Accepted'),
        ('declined', 'Declined'),
    ]
    status = models.CharField(max_length=20, choices=status_choices, default="pending")
    saved_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ['from_user', 'to_user']
