from django.db import models
from abstracts.models import AbstractBaseModel

class ContactMessage(AbstractBaseModel):
    name = models.CharField(max_length=100)
    email = models.EmailField()
    subject = models.CharField(max_length=255)
    message = models.TextField()
    is_read = models.BooleanField(default=False)

    def __str__(self):
        return f"Сообщение от {self.name}"