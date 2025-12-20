from rest_framework.serializers import (
    ModelSerializer,
    Serializer,
    SerializerMethodField,
    IntegerField,
    BooleanField,
)

from .models import Comment
from apps.accounts.serializers import UserDetailSerializer

class CommentQueryParamsSerializer(Serializer):
    news_id = IntegerField(required=False)
    user_id = IntegerField(required=False)
    parent_only = BooleanField(required=False, default=True)

class CommentBaseSerializer(ModelSerializer):
    class Meta:
        model = Comment
        fields = "__all__"


class CommentListSerializer(CommentBaseSerializer):
    user = UserDetailSerializer(read_only=True)
    has_replies = SerializerMethodField()

    class Meta:
        model = Comment
        fields = (
            "id",
            "text",
            "user",
            "created_at",
            "has_replies",
            "parent",
        )

    def get_has_replies(self, obj: Comment) -> bool:
        return obj.replies.exists()


class CommentDetailSerializer(CommentBaseSerializer):
    user = UserDetailSerializer(read_only=True)

    class Meta:
        model = Comment
        fields = "__all__"


class CommentCreateSerializer(CommentBaseSerializer):
    class Meta:
        model = Comment
        fields = (
            "id",
            "text",
            "news",
            "parent",
        )
        read_only_fields = ("id",)