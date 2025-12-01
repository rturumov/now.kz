from django.contrib.auth.models import AbstractUser
from django.db import models
from apps.abstracts.models import AbstractBaseModel

class User(AbstractUser, AbstractBaseModel):
    email = models.EmailField(unique=True)
    bio = models.TextField(blank=True, null=True)
    avatar = models.ImageField(upload_to='avatars/', blank=True, null=True)

    def __str__(self):
        return self.username


class Author(AbstractBaseModel):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='author_profile')
    description = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.user.username