from django.db.models import Count, Q
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, render
from django.utils.dateparse import parse_date
from rest_framework.viewsets import ViewSet
from rest_framework.permissions import AllowAny, IsAuthenticated, IsAuthenticatedOrReadOnly
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework import status
from .models import News, Category
from .serializers import NewsSerializer, CategorySerializer
from .permissions import IsAuthorOrReadOnly
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
                    filter=Q(news__is_published=True, news__deleted_at__isnull=True),
                )
            )
            .order_by("name")
        )
        return Response(CategorySerializer(qs, many=True).data)

    def retrieve(self, request, pk=None):
        category = get_object_or_404(Category, pk=pk, deleted_at__isnull=True)
        return Response(CategorySerializer(category).data)

    @action(detail=True, methods=["get"], permission_classes=[AllowAny])
    def news(self, request, pk=None):
        category = get_object_or_404(Category, pk=pk, deleted_at__isnull=True)

        qs = (
            News.objects
            .filter(category=category, is_published=True, deleted_at__isnull=True)
            .select_related("author", "author__user", "category")
            .order_by("-created_at")
        )

        return Response(NewsSerializer(qs, many=True).data)



class NewsViewSet(ViewSet):
    permission_classes = [IsAuthorOrReadOnly]

    def get_permissions(self):
        if self.action in ["list", "retrieve"]:
            return [AllowAny()]

        if self.action in ["create", "my_news"]:
            return [IsAuthenticated()]

        return [IsAuthorOrReadOnly()]

    def _base_qs(self):
        return (
            News.objects
            .filter(deleted_at__isnull=True)
            .select_related("author", "author__user", "category")
        )

    def list(self, request):
        user = request.user
        qs = self._base_qs()

        if not user.is_authenticated:
            qs = qs.filter(is_published=True)
        elif not hasattr(user, "author_profile"):
            qs = qs.filter(is_published=True)
        else:
            qs = qs.filter(Q(is_published=True) | Q(author=user.author_profile))

        params = request.query_params

        category_id = params.get("category_id")
        author_id = params.get("author_id")
        is_published = params.get("is_published")
        date_from = params.get("date_from")
        date_to = params.get("date_to")

        if category_id:
            qs = qs.filter(category_id=category_id)

        if author_id:
            qs = qs.filter(author_id=author_id)

        if is_published is not None:
            qs = qs.filter(is_published=is_published.lower() == "true")

        if date_from:
            qs = qs.filter(created_at__date__gte=parse_date(date_from))

        if date_to:
            qs = qs.filter(created_at__date__lte=parse_date(date_to))

        qs = qs.order_by("-created_at")
        return Response(NewsSerializer(qs, many=True).data)

    def retrieve(self, request, pk=None):
        news = get_object_or_404(self._base_qs(), pk=pk)
        return Response(NewsSerializer(news).data)

    def create(self, request):
        if not hasattr(request.user, "author_profile"):
            return Response({"detail": "Only authors can create news."}, status=status.HTTP_403_FORBIDDEN)

        serializer = NewsSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save(author=request.user.author_profile)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def update(self, request, pk=None):
        news = get_object_or_404(News, pk=pk, deleted_at__isnull=True)

        if not hasattr(request.user, "author_profile") or news.author != request.user.author_profile:
            return Response({"detail": "Permission denied."}, status=status.HTTP_403_FORBIDDEN)

        serializer = NewsSerializer(news, data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)

    def partial_update(self, request, pk=None):
        news = get_object_or_404(News, pk=pk, deleted_at__isnull=True)

        if not hasattr(request.user, "author_profile") or news.author != request.user.author_profile:
            return Response({"detail": "Permission denied."}, status=status.HTTP_403_FORBIDDEN)

        serializer = NewsSerializer(news, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)

    def destroy(self, request, pk=None):
        news = get_object_or_404(News, pk=pk, deleted_at__isnull=True)

        if not hasattr(request.user, "author_profile") or news.author != request.user.author_profile:
            return Response({"detail": "Permission denied."}, status=status.HTTP_403_FORBIDDEN)

        news.delete()  
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(detail=False, methods=["get"])
    def my_news(self, request):
        if not hasattr(request.user, "author_profile"):
            return Response({"detail": "You are not an author."}, status=status.HTTP_403_FORBIDDEN)

        qs = (
            self._base_qs()
            .filter(author=request.user.author_profile)
            .order_by("-created_at")
        )
        return Response(NewsSerializer(qs, many=True).data)

    @action(detail=True, methods=["post"])
    def publish(self, request, pk=None):
        news = get_object_or_404(News, pk=pk, deleted_at__isnull=True)

        if not hasattr(request.user, "author_profile") or news.author != request.user.author_profile:
            return Response({"detail": "Permission denied."}, status=status.HTTP_403_FORBIDDEN)

        news.is_published = True
        news.save(update_fields=["is_published"])
        return Response(NewsSerializer(news).data)

    @action(detail=True, methods=["post"])
    def unpublish(self, request, pk=None):
        news = get_object_or_404(News, pk=pk, deleted_at__isnull=True)

        if not hasattr(request.user, "author_profile") or news.author != request.user.author_profile:
            return Response({"detail": "Permission denied."}, status=status.HTTP_403_FORBIDDEN)

        news.is_published = False
        news.save(update_fields=["is_published"])
        return Response(NewsSerializer(news).data)


def home_page(request):
    return render(request, "home.html", {"title": "Главная"})


def news_list(request):
    all_news = (
        News.objects
        .filter(is_published=True, deleted_at__isnull=True)
        .select_related("author", "author__user", "category")
        .order_by("-published_at", "-created_at")
    )

    if request.headers.get("Accept") == "application/json":
        return JsonResponse(NewsSerializer(all_news, many=True).data, safe=False)

    return render(request, "news_list.html", {"news": all_news, "title": "Все Новости"})


def news_detail(request, news_id):
    news_item = get_object_or_404(
        News.objects.select_related("author", "author__user", "category"),
        id=news_id,
        is_published=True,
        deleted_at__isnull=True,
    )

    comments = (
        Comment.objects
        .filter(news=news_item, deleted_at__isnull=True, parent__isnull=True)
        .select_related("user")
        .prefetch_related("replies__user")
        .order_by("created_at")
    )

    for c in comments:
        c.active_replies = [r for r in c.replies.all() if r.deleted_at is None]

    if request.headers.get("Accept") == "application/json":
        return JsonResponse(NewsSerializer(news_item).data, safe=False)

    return render(
        request,
        "news_detail.html",
        {"news": news_item, "title": news_item.title, "comments": comments},
    )


def news_by_category(request, category_id):
    category = get_object_or_404(Category, id=category_id, deleted_at__isnull=True)

    news_items = (
        News.objects
        .filter(category=category, is_published=True, deleted_at__isnull=True)
        .select_related("author", "author__user", "category")
        .order_by("-published_at", "-created_at")
    )

    if request.headers.get("Accept") == "application/json":
        return JsonResponse(NewsSerializer(news_items, many=True).data, safe=False)

    return render(
        request,
        "news_by_category.html",
        {"category": category, "news": news_items, "title": f"Новости по категории: {category.name}"},
    )


def category_list(request):
    all_categories = (
        Category.objects
        .filter(deleted_at__isnull=True)
        .annotate(
            published_news_count=Count(
                "news",
                filter=Q(news__is_published=True, news__deleted_at__isnull=True),
            )
        )
        .order_by("name")
    )

    if request.headers.get("Accept") == "application/json":
        return JsonResponse(CategorySerializer(all_categories, many=True).data, safe=False)

    return render(request, "category_list.html", {"categories": all_categories, "title": "Все Категории"})