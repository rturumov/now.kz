from typing import Any
from django.db import models
from django.utils import timezone


class AbstractBaseModel(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    deleted_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        abstract = True

    def delete(self, *args: tuple[Any, ...], **kwargs: dict[str, Any]) -> None:
        self.deleted_at = timezone.now()
        self.save(update_fields=["deleted_at"])