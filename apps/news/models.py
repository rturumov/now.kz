from django.db import models
from apps.abstracts.models import AbstractBaseModel
from apps.accounts.models import Author

class Category(AbstractBaseModel):
    name = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.name


class News(AbstractBaseModel):
    title = models.CharField(max_length=255)
    content = models.TextField()
    image = models.ImageField(upload_to='news_images/', blank=True, null=True)
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, related_name='news')
    author = models.ForeignKey(Author, on_delete=models.SET_NULL, null=True, related_name='news')
    published_at = models.DateTimeField(auto_now_add=True)
    is_published = models.BooleanField(default=True)

    def __str__(self):
        return self.title