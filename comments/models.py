from django.db import models
from abstracts.models import AbstractBaseModel
from accounts.models import User
from news.models import News

class Comment(AbstractBaseModel):
    news = models.ForeignKey(News, on_delete=models.CASCADE, related_name='comments')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='comments')
    text = models.TextField()
    parent = models.ForeignKey('self', null=True, blank=True, on_delete=models.CASCADE, related_name='replies')

    def __str__(self):
        return f"{self.user.username} — {self.news.title[:30]}"