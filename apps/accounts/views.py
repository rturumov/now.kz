from django.shortcuts import get_object_or_404, render
from django.contrib.auth import get_user_model
from django.http import JsonResponse

from rest_framework.viewsets import ViewSet
from rest_framework.permissions import AllowAny, IsAuthenticated, IsAdminUser
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework import status

from .models import Author
from .serializers import (
    UserListSerializer,
    UserDetailSerializer,
    UserRegisterSerializer,
    AuthorListSerializer,
    AuthorDetailSerializer,
)

from apps.news.models import News
from apps.news.serializers import NewsListSerializer

User = get_user_model()

class UserViewSet(ViewSet):

    def _base_qs(self):
        return (
            User.objects
            .filter(is_active=True)
            .select_related("author_profile")
        )

    def get_permissions(self):
        if self.action == "register":
            return [AllowAny()]
        if self.action in ["list", "destroy"]:
            return [IsAdminUser()]
        return [IsAuthenticated()]

    def get_serializer_class(self):
        if self.action == "list":
            return UserListSerializer
        if self.action in ["retrieve", "me"]:
            return UserDetailSerializer
        if self.action == "register":
            return UserRegisterSerializer
        return UserDetailSerializer

    def list(self, request):
        users = self._base_qs().order_by("-date_joined")
        serializer = self.get_serializer_class()
        return Response(serializer(users, many=True).data)

    def retrieve(self, request, pk=None):
        user = get_object_or_404(self._base_qs(), pk=pk)
        serializer = self.get_serializer_class()
        return Response(serializer(user).data)

    @action(detail=False, methods=["post"], permission_classes=[AllowAny])
    def register(self, request):
        serializer = UserRegisterSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        return Response(
            UserDetailSerializer(user).data,
            status=status.HTTP_201_CREATED,
        )

    @action(detail=False, methods=["get", "put", "patch"])
    def me(self, request):
        user = request.user

        if request.method == "GET":
            return Response(UserDetailSerializer(user).data)

        serializer = UserDetailSerializer(
            user,
            data=request.data,
            partial=True,
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)

    @action(detail=True, methods=["post"])
    def set_password(self, request, pk=None):
        user = get_object_or_404(User, pk=pk)

        if user != request.user and not request.user.is_staff:
            return Response(
                {"detail": "Permission denied."},
                status=status.HTTP_403_FORBIDDEN,
            )

        password = request.data.get("password")
        if not password:
            return Response(
                {"password": ["This field is required."]},
                status=status.HTTP_400_BAD_REQUEST,
            )

        user.set_password(password)
        user.save(update_fields=["password"])
        return Response({"message": "Password updated"})

class AuthorViewSet(ViewSet):
    permission_classes = [AllowAny]

    def _base_qs(self):
        return (
            Author.objects
            .filter(deleted_at__isnull=True)
            .select_related("user")
        )

    def get_serializer_class(self):
        if self.action == "list":
            return AuthorListSerializer
        return AuthorDetailSerializer

    def list(self, request):
        authors = self._base_qs().order_by("user__email")
        serializer = self.get_serializer_class()
        return Response(serializer(authors, many=True).data)

    def retrieve(self, request, pk=None):
        author = get_object_or_404(self._base_qs(), pk=pk)
        serializer = self.get_serializer_class()
        return Response(serializer(author).data)

    @action(detail=True, methods=["get"])
    def news(self, request, pk=None):
        author = get_object_or_404(self._base_qs(), pk=pk)

        qs = (
            News.objects
            .filter(
                author=author,
                is_published=True,
                deleted_at__isnull=True,
            )
            .select_related("category")
            .order_by("-created_at")
        )

        return Response(NewsListSerializer(qs, many=True).data)

    @action(detail=False, methods=["post"], permission_classes=[IsAuthenticated])
    def become_author(self, request):
        if hasattr(request.user, "author_profile"):
            return Response(
                {"detail": "Already an author."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        author = Author.objects.create(
            user=request.user,
            description=request.data.get("description", ""),
        )

        return Response(
            AuthorDetailSerializer(author).data,
            status=status.HTTP_201_CREATED,
        )

def author_list(request):
    authors = (
        Author.objects
        .filter(user__is_active=True, deleted_at__isnull=True)
        .select_related("user")
        .order_by("user__email")
    )

    if request.headers.get("Accept") == "application/json":
        return JsonResponse(
            AuthorListSerializer(authors, many=True).data,
            safe=False,
        )

    return render(
        request,
        "author_list.html",
        {"authors": authors, "title": "Список Авторов"},
    )


def author_detail(request, username):
    user_profile = get_object_or_404(
        User.objects.select_related("author_profile"),
        email=username,
        is_active=True,
    )

    author_profile = getattr(user_profile, "author_profile", None)

    if request.headers.get("Accept") == "application/json":
        return JsonResponse(
            {
                "user": UserDetailSerializer(user_profile).data,
                "author": (
                    AuthorDetailSerializer(author_profile).data
                    if author_profile else None
                ),
            }
        )

    return render(
        request,
        "author_detail.html",
        {
            "user_data": user_profile,
            "author_data": author_profile,
            "title": f"Профиль: {user_profile.email}",
        },
    )