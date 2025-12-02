from rest_framework import serializers
from .models import News, Category


class CategorySerializer(serializers.ModelSerializer):
    published_news_count = serializers.IntegerField(read_only=True)

    class Meta:
        model = Category
        fields = ['id', 'name', 'published_news_count']
        read_only_fields = ['id']


class NewsSerializer(serializers.ModelSerializer):
    category = CategorySerializer(read_only=True)
    category_id = serializers.PrimaryKeyRelatedField(
        queryset=Category.objects.all(),
        source='category',
        write_only=True,
        required=False,
        allow_null=True
    )
    author_name = serializers.CharField(source='author.__str__', read_only=True)

    class Meta:
        model = News
        fields = [
            'id', 'title', 'content', 'image', 
            'category', 'category_id', 'author', 'author_name',
            'published_at', 'is_published', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'author', 'published_at', 'created_at', 'updated_at']

    def validate(self, data):
        if 'title' in data and not data['title'].strip():
            raise serializers.ValidationError({'title': 'Заголовок не может быть пустым.'})
        
        if 'content' in data and not data['content'].strip():
            raise serializers.ValidationError({'content': 'Содержание не может быть пустым.'})
        
        return data

    def create(self, validated_data):
        request = self.context.get('request')
        if request and hasattr(request.user, 'author_profile'):
            validated_data['author'] = request.user.author_profile
        
        return super().create(validated_data)