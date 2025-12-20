from rest_framework.serializers import (
    ModelSerializer,
    SerializerMethodField,
    CharField,
)
from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password

from .models import Author

User = get_user_model()

class UserBaseSerializer(ModelSerializer):
    class Meta:
        model = User
        fields = "__all__"


class UserListSerializer(UserBaseSerializer):
    is_author = SerializerMethodField()

    class Meta:
        model = User
        fields = (
            "id",
            "email",
            "first_name",
            "last_name",
            "is_author",
        )

    def get_is_author(self, obj: User) -> bool:
        return hasattr(obj, "author_profile")


class UserDetailSerializer(UserBaseSerializer):
    is_author = SerializerMethodField()

    class Meta:
        model = User
        fields = "__all__"
        read_only_fields = (
            "id",
            "is_active",
            "is_staff",
            "is_superuser",
        )

    def get_is_author(self, obj: User) -> bool:
        return hasattr(obj, "author_profile")


class UserRegisterSerializer(ModelSerializer):
    password = CharField(write_only=True, validators=[validate_password])
    password2 = CharField(write_only=True)

    class Meta:
        model = User
        fields = (
            "email",
            "password",
            "password2",
        )

    def validate(self, attrs):
        if attrs["password"] != attrs["password2"]:
            raise ValueError("Passwords do not match")
        return attrs

    def create(self, validated_data):
        validated_data.pop("password2")
        return User.objects.create_user(**validated_data)

class AuthorBaseSerializer(ModelSerializer):
    class Meta:
        model = Author
        fields = "__all__"


class AuthorListSerializer(AuthorBaseSerializer):
    user_email = SerializerMethodField()
    news_count = SerializerMethodField()

    class Meta:
        model = Author
        fields = (
            "id",
            "user_email",
            "description",
            "news_count",
        )

    def get_user_email(self, obj: Author) -> str:
        return obj.user.email

    def get_news_count(self, obj: Author) -> int:
        from apps.news.models import News
        return News.objects.filter(author=obj, is_published=True).count()


class AuthorDetailSerializer(AuthorBaseSerializer):
    class Meta:
        model = Author
        fields = "__all__"