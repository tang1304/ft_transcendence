from django.db import models
from django.contrib.auth.models import AbstractUser
from PIL import Image

# Create your models here.

class User(AbstractUser):
    username = models.CharField(max_length=255, unique=True)
    password = models.CharField(max_length=255)
    email = models.EmailField(_('email address'), max_length=255, unique=True)
    image = models.ImageField(upload_to='profile_pics/', default='default_pp.jpg')

    REQUIRED_FIELDS = []

    def save(self, *args, **kwargs):
        super().save()

        img = Image.open(self.avatar.path)

        if img.height > 200 or img.width > 200:
            new_img = (200, 200)
            img.thumbnail(new_img)
            img.save(self.avatar.path)
