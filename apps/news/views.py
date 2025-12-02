from django.shortcuts import get_object_or_404, render
from django.db.models import Count, Q
from django.http import JsonResponse
from rest_framework import viewsets, permissions, status, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from .models import News, Category
from .serializers import NewsSerializer, CategorySerializer

class CategoryViewSet(viewsets.ModelViewSet):
    queryset = Category.objects.annotate(
        published_news_count=Count('news', filter=Q(news__is_published=True))
    ).order_by('name')
    serializer_class = CategorySerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    filter_backends = [filters.SearchFilter]
    search_fields = ['name']

    @action(detail=True, methods=['get'])
    def news(self, request, pk=None):
        category = self.get_object()
        news_items = News.objects.filter(
            category=category, 
            is_published=True
        ).order_by('-published_at')
        
        page = self.paginate_queryset(news_items)
        if page is not None:
            serializer = NewsSerializer(page, many=True)
            return self.get_paginated_response(serializer.data)
            
        serializer = NewsSerializer(news_items, many=True)
        return Response(serializer.data)


class NewsViewSet(viewsets.ModelViewSet):
    queryset = News.objects.filter(is_published=True).order_by('-published_at')
    serializer_class = NewsSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['title', 'content']
    ordering_fields = ['published_at', 'title']
    ordering = ['-published_at']

    def get_queryset(self):
        if self.request.user.is_authenticated and hasattr(self.request.user, 'author_profile'):
            return News.objects.filter(
                Q(is_published=True) | 
                Q(author__user=self.request.user)
            ).order_by('-published_at')
        
        return News.objects.filter(is_published=True).order_by('-published_at')

    def perform_create(self, serializer):
        if hasattr(self.request.user, 'author_profile'):
            serializer.save(author=self.request.user.author_profile)
        else:
            serializer.save()

    @action(detail=False, methods=['get'])
    def my_news(self, request):
        if not hasattr(request.user, 'author_profile'):
            return Response(
                {'detail': 'Вы не являетесь автором.'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        news_items = News.objects.filter(
            author__user=request.user
        ).order_by('-published_at')
        
        page = self.paginate_queryset(news_items)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
            
        serializer = self.get_serializer(news_items, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=['post'])
    def publish(self, request, pk=None):
        news = self.get_object()
        
        if not hasattr(request.user, 'author_profile') or news.author.user != request.user:
            return Response(
                {'detail': 'У вас нет прав для публикации этой новости.'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        news.is_published = True
        news.save()
        
        serializer = self.get_serializer(news)
        return Response(serializer.data)

    @action(detail=True, methods=['post'])
    def unpublish(self, request, pk=None):
        news = self.get_object()
        
        if not hasattr(request.user, 'author_profile') or news.author.user != request.user:
            return Response(
                {'detail': 'У вас нет прав для снятия этой новости с публикации.'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        news.is_published = False
        news.save()
        
        serializer = self.get_serializer(news)
        return Response(serializer.data)

def news_list(request):
    all_news = News.objects.filter(is_published=True).order_by('-published_at')

    if request.headers.get('Accept') == 'application/json':
        serializer = NewsSerializer(all_news, many=True)
        return JsonResponse(serializer.data, safe=False)

    context = {
        'news': all_news,
        'title': 'Все Новости'
    }
    return render(request, 'news_list.html', context)


def news_detail(request, news_id):
    news_item = get_object_or_404(News, id=news_id, is_published=True)

    if request.headers.get('Accept') == 'application/json':
        serializer = NewsSerializer(news_item)
        return JsonResponse(serializer.data, safe=False)

    context = {
        'news': news_item,
        'title': news_item.title
    }
    return render(request, 'news_detail.html', context)


def news_by_category(request, category_id):
    category = get_object_or_404(Category, id=category_id)
    news_items = News.objects.filter(category=category, is_published=True).order_by('-published_at')

    if request.headers.get('Accept') == 'application/json':
        serializer = NewsSerializer(news_items, many=True)
        return JsonResponse(serializer.data, safe=False)

    context = {
        'category': category,
        'news': news_items,
        'title': f'Новости по категории: {category.name}'
    }
    return render(request, 'news_by_category.html', context)


def category_list(request):
    all_categories = Category.objects.annotate(
        published_news_count=Count('news', filter=Q(news__is_published=True))
    ).order_by('name')

    if request.headers.get('Accept') == 'application/json':
        serializer = CategorySerializer(all_categories, many=True)
        return JsonResponse(serializer.data, safe=False)

    context = {
        'categories': all_categories,
        'title': 'Все Категории'
    }
    return render(request, 'category_list.html', context)


def home_page(request):
    return render(request, 'home.html', {'title': 'Главная Страница'})