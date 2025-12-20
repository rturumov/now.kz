from typing import Any
from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.db import models
from apps.abstracts.models import AbstractBaseModel


class UserManager(BaseUserManager):
    def create_user(self, email: str, password: str | None = None, **extra_fields: Any):
        if not email:
            raise ValueError("Email is required")

        email = self.normalize_email(email)
        extra_fields.setdefault("username", email.split("@")[0])

        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(
        self, email: str, password: str | None = None, **extra_fields: Any
    ):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        extra_fields.setdefault("is_active", True)

        return self.create_user(email=email, password=password, **extra_fields)


class User(AbstractUser, AbstractBaseModel):
    email = models.EmailField(
        unique=True,
        db_index=True,
        verbose_name="Email address",
    )

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["username"]

    objects = UserManager()

    class Meta:
        ordering = ["-created_at"]
        verbose_name = "User"
        verbose_name_plural = "Users"

    def __str__(self) -> str:
        return self.email
    
class Author(AbstractBaseModel):
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name="author_profile",
    )
    description = models.TextField(blank=True, null=True)

    class Meta:
        verbose_name = "Author"
        verbose_name_plural = "Authors"

    def __str__(self) -> str:
        return self.user.email