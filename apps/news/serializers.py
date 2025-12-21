from rest_framework.exceptions import ValidationError
from rest_framework.serializers import (
    ModelSerializer,
    Serializer,
    SerializerMethodField,
    IntegerField,
    BooleanField,
    DateField,
)

from .models import News, Category
from apps.accounts.models import Author

class NewsQueryParamsSerializer(Serializer):
    category_id = IntegerField(required=False)
    author_id = IntegerField(required=False)
    is_published = BooleanField(required=False)
    date_from = DateField(required=False)
    date_to = DateField(required=False)

    def validate(self, attrs):
        if (
            attrs.get("date_from")
            and attrs.get("date_to")
            and attrs["date_from"] > attrs["date_to"]
        ):
            raise ValidationError({
                "date_from": "date_from cannot be greater than date_to"
            })
        return attrs

class CategoryListSerializer(ModelSerializer):
    published_news_count = IntegerField(read_only=True)

    class Meta:
        model = Category
        fields = (
            "id",
            "name",
            "published_news_count",
        )

class AuthorForeignSerializer(ModelSerializer):
    email = SerializerMethodField()

    class Meta:
        model = Author
        fields = (
            "id",
            "email",
        )

    def get_email(self, obj: Author) -> str:
        return obj.user.email

class NewsListSerializer(ModelSerializer):
    author = AuthorForeignSerializer(read_only=True)
    category_name = SerializerMethodField()

    class Meta:
        model = News
        fields = (
            "id",
            "title",
            "category_name",
            "author",
            "is_published",
            "created_at",
        )

    def get_category_name(self, obj: News):
        return obj.category.name if obj.category else None


class NewsDetailSerializer(ModelSerializer):
    author = AuthorForeignSerializer(read_only=True)

    class Meta:
        model = News
        fields = (
            "id",
            "title",
            "content",
            "image",
            "author",
            "category",
            "is_published",
            "published_at",
            "created_at",
            "updated_at",
        )


class NewsCreateSerializer(ModelSerializer):
    class Meta:
        model = News
        fields = (
            "title",
            "content",
            "image",
            "category",
        )


class NewsUpdateSerializer(ModelSerializer):
    class Meta:
        model = News
        fields = (
            "title",
            "content",
            "image",
            "category",
            "is_published",
        )