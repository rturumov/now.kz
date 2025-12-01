# apps/news/serializers.py
from rest_framework import serializers
from .models import News, Category

class CategorySerializer(serializers.ModelSerializer):
    published_news_count = serializers.IntegerField(read_only=True)

    class Meta:
        model = Category
        fields = ['id', 'name', 'published_news_count']


class NewsSerializer(serializers.ModelSerializer):
    category = CategorySerializer(read_only=True)
    
    class Meta:
        model = News
        fields = ['id', 'title', 'content', 'category', 'author', 'published_at', 'is_published']
