from django.shortcuts import get_object_or_404, render
from rest_framework import viewsets, permissions, status, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from django.http import JsonResponse
from .models import Comment
from apps.news.models import News
from .serializers import CommentSerializer
from .permissions import IsCommentOwnerOrReadOnly

class CommentViewSet(viewsets.ModelViewSet):
    serializer_class = CommentSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly, IsCommentOwnerOrReadOnly]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['text', 'user__username']
    ordering_fields = ['created_at', 'updated_at']
    ordering = ['created_at'] 

    def get_queryset(self):
        queryset = Comment.objects.all()
        
        news_id = self.request.query_params.get('news_id')
        if news_id:
            queryset = queryset.filter(news_id=news_id)
        
        parent_only = self.request.query_params.get('parent_only', 'true').lower() == 'true'
        if parent_only:
            queryset = queryset.filter(parent__isnull=True)
        
        user_id = self.request.query_params.get('user_id')
        if user_id:
            queryset = queryset.filter(user_id=user_id)
        
        return queryset.select_related('user', 'news', 'parent')

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    @action(detail=True, methods=['get'])
    def replies(self, request, pk=None):
        comment = self.get_object()
        replies = comment.replies.all()
        
        page = self.paginate_queryset(replies)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
            
        serializer = self.get_serializer(replies, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=['post'])
    def reply(self, request, pk=None):
        comment = self.get_object()
        
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        reply = serializer.save(
            user=request.user,
            news=comment.news,
            parent=comment
        )
        
        return Response(
            self.get_serializer(reply).data,
            status=status.HTTP_201_CREATED
        )

    @action(detail=False, methods=['get'])
    def news_comments(self, request):
        news_id = request.query_params.get('news_id')
        if not news_id:
            return Response(
                {'detail': 'Не указан news_id параметр.'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            news = News.objects.get(id=news_id)
        except News.DoesNotExist:
            return Response(
                {'detail': 'Новость не найдена.'},
                status=status.HTTP_404_NOT_FOUND
            )
        
        comments = Comment.objects.filter(news=news, parent__isnull=True)
        
        page = self.paginate_queryset(comments)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
            
        serializer = self.get_serializer(comments, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def my_comments(self, request):
        comments = Comment.objects.filter(user=request.user)
        
        page = self.paginate_queryset(comments)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
            
        serializer = self.get_serializer(comments, many=True)
        return Response(serializer.data)

def comment_list(request, news_id):
    news_item = get_object_or_404(News, id=news_id)
    comments = Comment.objects.filter(news=news_item, parent__isnull=True)

    if request.headers.get('Accept') == 'application/json':
        serializer = CommentSerializer(comments, many=True)
        return JsonResponse(serializer.data, safe=False)

    context = {
        'news': news_item,
        'comments': comments,
        'title': f'Комментарии к новости: {news_item.title}'
    }
    return render(request, 'comment_list.html', context)


def comment_detail(request, comment_id):
    comment = get_object_or_404(Comment, id=comment_id)

    if request.headers.get('Accept') == 'application/json':
        serializer = CommentSerializer(comment)
        return JsonResponse(serializer.data, safe=False)

    context = {
        'comment': comment,
        'replies': comment.replies.all(),
        'title': f'Комментарий пользователя: {comment.user.username}'
    }
    return render(request, 'comment_detail.html', context)