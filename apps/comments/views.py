from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, render
from django.http import JsonResponse

from rest_framework.viewsets import ViewSet
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework import status

from .models import Comment
from .permissions import IsCommentOwnerOrReadOnly
from .serializers import (
    CommentListSerializer,
    CommentDetailSerializer,
    CommentCreateSerializer,
    CommentQueryParamsSerializer,
)

from apps.news.models import News


class CommentViewSet(ViewSet):
    permission_classes = [IsCommentOwnerOrReadOnly]

    def get_permissions(self):
        if self.action in ["list", "retrieve", "news_comments"]:
            return [AllowAny()]
        return [IsAuthenticated()]

    def get_serializer_class(self):
        if self.action == "list":
            return CommentListSerializer
        if self.action == "retrieve":
            return CommentDetailSerializer
        if self.action in ["create", "reply"]:
            return CommentCreateSerializer
        return CommentDetailSerializer

    def _base_qs(self):
        return (
            Comment.objects
            .filter(deleted_at__isnull=True)
            .select_related("user", "news", "parent")
            .prefetch_related("replies__user")
        )

    def list(self, request):
        params = CommentQueryParamsSerializer(data=request.query_params)
        params.is_valid(raise_exception=True)
        data = params.validated_data

        qs = self._base_qs()

        if "news_id" in data:
            qs = qs.filter(news_id=data["news_id"])

        if "user_id" in data:
            qs = qs.filter(user_id=data["user_id"])

        if data.get("parent_only", True):
            qs = qs.filter(parent__isnull=True)

        qs = qs.order_by("created_at")
        serializer = self.get_serializer_class()
        return Response(serializer(qs, many=True).data)

    def retrieve(self, request, pk=None):
        comment = get_object_or_404(self._base_qs(), pk=pk)
        serializer = self.get_serializer_class()
        return Response(serializer(comment).data)

    def create(self, request):
        serializer = CommentCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        news = get_object_or_404(
            News,
            pk=serializer.validated_data["news"].id,
            deleted_at__isnull=True,
        )

        comment = serializer.save(
            user=request.user,
            news=news,
        )

        return Response(
            CommentDetailSerializer(comment).data,
            status=status.HTTP_201_CREATED,
        )

    def destroy(self, request, pk=None):
        comment = get_object_or_404(Comment, pk=pk, deleted_at__isnull=True)

        if comment.user != request.user:
            return Response(
                {"detail": "Permission denied"},
                status=status.HTTP_403_FORBIDDEN,
            )

        comment.delete()
        comment.replies.update(deleted_at=comment.deleted_at)

        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(detail=True, methods=["post"])
    def reply(self, request, pk=None):
        parent = get_object_or_404(Comment, pk=pk, deleted_at__isnull=True)

        serializer = CommentCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        reply = serializer.save(
            user=request.user,
            news=parent.news,
            parent=parent,
        )

        return Response(
            CommentDetailSerializer(reply).data,
            status=status.HTTP_201_CREATED,
        )

    @action(detail=True, methods=["get"])
    def replies(self, request, pk=None):
        parent = get_object_or_404(Comment, pk=pk, deleted_at__isnull=True)

        replies = (
            self._base_qs()
            .filter(parent=parent)
            .order_by("created_at")
        )

        return Response(CommentListSerializer(replies, many=True).data)

    @action(detail=False, methods=["get"])
    def news_comments(self, request):
        news_id = request.query_params.get("news_id")
        if not news_id:
            return Response(
                {"detail": "news_id is required"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        news = get_object_or_404(
            News,
            pk=news_id,
            deleted_at__isnull=True,
        )

        comments = (
            self._base_qs()
            .filter(news=news, parent__isnull=True)
            .order_by("created_at")
        )

        return Response(CommentListSerializer(comments, many=True).data)

    @action(detail=False, methods=["get"])
    def my_comments(self, request):
        comments = (
            self._base_qs()
            .filter(user=request.user)
            .order_by("-created_at")
        )
        return Response(CommentListSerializer(comments, many=True).data)

@login_required
def my_comments_list(request):
    comments = (
        Comment.objects
        .filter(user=request.user, deleted_at__isnull=True)
        .select_related("news", "user")
        .order_by("-created_at")
    )

    return render(
        request,
        "my_comments_list.html",
        {
            "comments": comments,
            "title": "Мои комментарии",
        },
    )


def comment_list(request, news_id):
    news_item = get_object_or_404(
        News,
        pk=news_id,
        deleted_at__isnull=True,
    )

    comments = (
        Comment.objects
        .filter(
            news=news_item,
            parent__isnull=True,
            deleted_at__isnull=True,
        )
        .select_related("user", "news")
        .prefetch_related("replies__user")
        .order_by("created_at")
    )

    if request.headers.get("Accept") == "application/json":
        return JsonResponse(
            CommentListSerializer(comments, many=True).data,
            safe=False,
        )

    return render(
        request,
        "comment_list.html",
        {
            "news": news_item,
            "comments": comments,
            "title": f"Комментарии к новости: {news_item.title}",
        },
    )


def comment_detail(request, comment_id):
    comment = get_object_or_404(
        Comment,
        pk=comment_id,
        deleted_at__isnull=True,
    )

    replies = (
        comment.replies
        .filter(deleted_at__isnull=True)
        .select_related("user")
    )

    if request.headers.get("Accept") == "application/json":
        return JsonResponse(
            CommentDetailSerializer(comment).data,
            safe=False,
        )

    return render(
        request,
        "comment_detail.html",
        {
            "comment": comment,
            "replies": replies,
            "title": f"Комментарий пользователя: {comment.user.username}",
        },
    )