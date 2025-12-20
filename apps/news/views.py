from django.db.models import Count, Q
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, render

from rest_framework.viewsets import ViewSet
from rest_framework.permissions import AllowAny, IsAuthenticated, IsAuthenticatedOrReadOnly
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework import status

from .models import News, Category
from .permissions import IsAuthorOrReadOnly
from .serializers import (
    CategoryListSerializer,
    NewsListSerializer,
    NewsDetailSerializer,
    NewsCreateSerializer,
    NewsUpdateSerializer,
    NewsQueryParamsSerializer,
)

from apps.comments.models import Comment

class CategoryViewSet(ViewSet):
    permission_classes = [IsAuthenticatedOrReadOnly]

    def list(self, request):
        qs = (
            Category.objects
            .filter(deleted_at__isnull=True)
            .annotate(
                published_news_count=Count(
                    "news",
                    filter=Q(
                        news__is_published=True,
                        news__deleted_at__isnull=True,
                    ),
                )
            )
            .order_by("name")
        )
        serializer = CategoryListSerializer(qs, many=True)
        return Response(serializer.data)

    def retrieve(self, request, pk=None):
        category = get_object_or_404(
            Category,
            pk=pk,
            deleted_at__isnull=True,
        )
        serializer = CategoryListSerializer(category)
        return Response(serializer.data)

    @action(detail=True, methods=["get"], permission_classes=[AllowAny])
    def news(self, request, pk=None):
        category = get_object_or_404(
            Category,
            pk=pk,
            deleted_at__isnull=True,
        )

        qs = (
            News.objects
            .filter(
                category=category,
                is_published=True,
                deleted_at__isnull=True,
            )
            .select_related("author", "author__user", "category")
            .order_by("-created_at")
        )

        serializer = NewsListSerializer(qs, many=True)
        return Response(serializer.data)

class NewsViewSet(ViewSet):
    permission_classes = [IsAuthorOrReadOnly]

    def get_permissions(self):
        if self.action in ["list", "retrieve"]:
            return [AllowAny()]
        if self.action in ["create", "my_news"]:
            return [IsAuthenticated()]
        return [IsAuthorOrReadOnly()]

    def get_queryset(self):
        return (
            News.objects
            .filter(deleted_at__isnull=True)
            .select_related("author", "author__user", "category")
        )

    def list(self, request):
        user = request.user
        qs = self.get_queryset()

        if not user.is_authenticated:
            qs = qs.filter(is_published=True)
        elif not hasattr(user, "author_profile"):
            qs = qs.filter(is_published=True)
        else:
            qs = qs.filter(
                Q(is_published=True) |
                Q(author=user.author_profile)
            )

        params_serializer = NewsQueryParamsSerializer(
            data=request.query_params
        )
        params_serializer.is_valid(raise_exception=True)
        params = params_serializer.validated_data

        if "category_id" in params:
            qs = qs.filter(category_id=params["category_id"])

        if "author_id" in params:
            qs = qs.filter(author_id=params["author_id"])

        if "is_published" in params:
            qs = qs.filter(is_published=params["is_published"])

        if "date_from" in params:
            qs = qs.filter(created_at__date__gte=params["date_from"])

        if "date_to" in params:
            qs = qs.filter(created_at__date__lte=params["date_to"])

        qs = qs.order_by("-created_at")

        serializer = NewsListSerializer(qs, many=True)
        return Response(serializer.data)

    def retrieve(self, request, pk=None):
        news = get_object_or_404(
            self.get_queryset(),
            pk=pk,
        )
        serializer = NewsDetailSerializer(news)
        return Response(serializer.data)

    def create(self, request):
        if not hasattr(request.user, "author_profile"):
            return Response(
                {"detail": "Only authors can create news."},
                status=status.HTTP_403_FORBIDDEN,
            )

        serializer = NewsCreateSerializer(
            data=request.data,
            context={"request": request},
        )
        serializer.is_valid(raise_exception=True)
        news = serializer.save(
            author=request.user.author_profile
        )
        return Response(
            NewsDetailSerializer(news).data,
            status=status.HTTP_201_CREATED,
        )

    def update(self, request, pk=None):
        news = get_object_or_404(
            News,
            pk=pk,
            deleted_at__isnull=True,
        )

        if news.author != getattr(request.user, "author_profile", None):
            return Response(
                {"detail": "Permission denied."},
                status=status.HTTP_403_FORBIDDEN,
            )

        serializer = NewsUpdateSerializer(
            news,
            data=request.data,
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(
            NewsDetailSerializer(news).data
        )

    def partial_update(self, request, pk=None):
        news = get_object_or_404(
            News,
            pk=pk,
            deleted_at__isnull=True,
        )

        if news.author != getattr(request.user, "author_profile", None):
            return Response(
                {"detail": "Permission denied."},
                status=status.HTTP_403_FORBIDDEN,
            )

        serializer = NewsUpdateSerializer(
            news,
            data=request.data,
            partial=True,
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(
            NewsDetailSerializer(news).data
        )

    def destroy(self, request, pk=None):
        news = get_object_or_404(
            News,
            pk=pk,
            deleted_at__isnull=True,
        )

        if news.author != getattr(request.user, "author_profile", None):
            return Response(
                {"detail": "Permission denied."},
                status=status.HTTP_403_FORBIDDEN,
            )

        news.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(detail=False, methods=["get"])
    def my_news(self, request):
        if not hasattr(request.user, "author_profile"):
            return Response(
                {"detail": "You are not an author."},
                status=status.HTTP_403_FORBIDDEN,
            )

        qs = (
            self.get_queryset()
            .filter(author=request.user.author_profile)
            .order_by("-created_at")
        )
        serializer = NewsListSerializer(qs, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=["post"])
    def publish(self, request, pk=None):
        news = get_object_or_404(
            News,
            pk=pk,
            deleted_at__isnull=True,
        )

        if news.author != getattr(request.user, "author_profile", None):
            return Response(
                {"detail": "Permission denied."},
                status=status.HTTP_403_FORBIDDEN,
            )

        news.is_published = True
        news.save(update_fields=["is_published"])
        return Response(
            NewsDetailSerializer(news).data
        )

    @action(detail=True, methods=["post"])
    def unpublish(self, request, pk=None):
        news = get_object_or_404(
            News,
            pk=pk,
            deleted_at__isnull=True,
        )

        if news.author != getattr(request.user, "author_profile", None):
            return Response(
                {"detail": "Permission denied."},
                status=status.HTTP_403_FORBIDDEN,
            )

        news.is_published = False
        news.save(update_fields=["is_published"])
        return Response(
            NewsDetailSerializer(news).data
        )

def home_page(request):
    return render(request, "home.html", {"title": "Главная"})


def news_list(request):
    qs = (
        News.objects
        .filter(is_published=True, deleted_at__isnull=True)
        .select_related("author", "author__user", "category")
        .order_by("-published_at", "-created_at")
    )

    if request.headers.get("Accept") == "application/json":
        return JsonResponse(
            NewsListSerializer(qs, many=True).data,
            safe=False,
        )

    return render(
        request,
        "news_list.html",
        {"news": qs, "title": "Все Новости"},
    )


def news_detail(request, news_id):
    news = get_object_or_404(
        News.objects.select_related(
            "author",
            "author__user",
            "category",
        ),
        id=news_id,
        is_published=True,
        deleted_at__isnull=True,
    )

    comments = (
        Comment.objects
        .filter(
            news=news,
            deleted_at__isnull=True,
            parent__isnull=True,
        )
        .select_related("user")
        .prefetch_related("replies__user")
        .order_by("created_at")
    )

    if request.headers.get("Accept") == "application/json":
        return JsonResponse(
            NewsDetailSerializer(news).data,
            safe=False,
        )

    return render(
        request,
        "news_detail.html",
        {
            "news": news,
            "title": news.title,
            "comments": comments,
        },
    )
    
def category_list(request):
    qs = (
        Category.objects
        .filter(deleted_at__isnull=True)
        .annotate(
            published_news_count=Count(
                "news",
                filter=Q(
                    news__is_published=True,
                    news__deleted_at__isnull=True,
                ),
            )
        )
        .order_by("name")
    )

    if request.headers.get("Accept") == "application/json":
        return JsonResponse(
            CategoryListSerializer(qs, many=True).data,
            safe=False,
        )

    return render(
        request,
        "category_list.html",
        {
            "categories": qs,
            "title": "Все категории",
        },
    )
    
def news_by_category(request, category_id):
    category = get_object_or_404(
        Category,
        id=category_id,
        deleted_at__isnull=True,
    )

    qs = (
        News.objects
        .filter(
            category=category,
            is_published=True,
            deleted_at__isnull=True,
        )
        .select_related("author", "author__user", "category")
        .order_by("-published_at", "-created_at")
    )

    if request.headers.get("Accept") == "application/json":
        return JsonResponse(
            NewsListSerializer(qs, many=True).data,
            safe=False,
        )

    return render(
        request,
        "news_by_category.html",
        {
            "category": category,
            "news": qs,
            "title": f"Новости по категории: {category.name}",
        },
    )