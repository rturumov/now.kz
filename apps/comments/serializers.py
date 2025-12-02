from rest_framework import serializers
from django.contrib.auth import get_user_model

from apps.news.models import News
from .models import Comment
from apps.accounts.serializers import UserSerializer

User = get_user_model()


class CommentSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    replies = serializers.SerializerMethodField()
    user_id = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.all(),
        source='user',
        write_only=True,
        required=False
    )
    news_id = serializers.PrimaryKeyRelatedField(
        queryset=News.objects.all(),
        source='news',
        write_only=True
    )
    parent_id = serializers.PrimaryKeyRelatedField(
        queryset=Comment.objects.all(),
        source='parent',
        write_only=True,
        required=False,
        allow_null=True
    )
    has_replies = serializers.SerializerMethodField()

    class Meta:
        model = Comment
        fields = [
            'id', 'news', 'news_id', 'user', 'user_id',
            'text', 'parent', 'parent_id', 'replies',
            'has_replies', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']
        extra_kwargs = {
            'news': {'required': False},
            'parent': {'required': False}
        }

    def get_replies(self, obj):
        return list(obj.replies.values_list('id', flat=True))

    def get_has_replies(self, obj):
        return obj.replies.exists()

    def validate(self, data):
        if 'text' in data and not data['text'].strip():
            raise serializers.ValidationError({'text': 'Текст комментария не может быть пустым.'})
        
        if 'text' in data and len(data['text']) > 5000:
            raise serializers.ValidationError({'text': 'Комментарий слишком длинный (максимум 5000 символов).'})
        
        if 'parent' in data and data['parent']:
            if 'news' in data and data['news'] != data['parent'].news:
                raise serializers.ValidationError({
                    'parent': 'Ответ должен быть к той же новости, что и родительский комментарий.'
                })
        
        return data

    def create(self, validated_data):
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            if 'user' not in validated_data:
                validated_data['user'] = request.user
        
        return super().create(validated_data)