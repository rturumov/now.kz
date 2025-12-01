from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.db import models
from apps.abstracts.models import AbstractBaseModel

class UserManager(BaseUserManager):
    def create_user(self, username, email, password=None, **extra_fields):
        if not email:
            raise ValueError("Email must be provided")
        email = self.normalize_email(email)
        user = self.model(username=username, email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, username, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        return self.create_user(username, email, password, **extra_fields)


class User(AbstractUser, AbstractBaseModel):
    email = models.EmailField(unique=True)
    bio = models.TextField(blank=True, null=True)
    avatar = models.ImageField(upload_to='avatars/', blank=True, null=True)

    objects = UserManager()

    USERNAME_FIELD = 'username'  
    REQUIRED_FIELDS = ['email']  

    def __str__(self):
        return self.username


class Author(AbstractBaseModel):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='author_profile')
    description = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.user.username
