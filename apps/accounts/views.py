from django.shortcuts import get_object_or_404, render
from django.contrib.auth import get_user_model
from rest_framework import viewsets, permissions, status, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from django.http import JsonResponse
from .models import User, Author
from .serializers import UserSerializer, AuthorSerializer

User = get_user_model()

class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.filter(is_active=True).order_by('-date_joined')
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [filters.SearchFilter]
    search_fields = ['username', 'email']
    
    def get_permissions(self):
        if self.action in ['create', 'register']:
            return [AllowAny()]
        elif self.action in ['retrieve', 'update', 'partial_update', 'me']:
            return [permissions.IsAuthenticated()]
        elif self.action in ['list', 'destroy']:
            return [permissions.IsAdminUser()]
        return super().get_permissions()

    def get_queryset(self):
        user = self.request.user
        if user.is_staff:
            return User.objects.all()
        return User.objects.filter(id=user.id)

    def get_serializer_class(self):
        if self.action == 'create':
            from .serializers import UserRegisterSerializer
            return UserRegisterSerializer
        return super().get_serializer_class()

    @action(detail=False, methods=['post'], permission_classes=[AllowAny])
    def register(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        
        return Response({
            'user': UserSerializer(user).data,
            'message': 'Пользователь успешно зарегистрирован'
        }, status=status.HTTP_201_CREATED)

    @action(detail=False, methods=['get', 'put', 'patch'])
    def me(self, request):
        user = request.user
        if request.method == 'GET':
            serializer = self.get_serializer(user)
            return Response(serializer.data)

        serializer = self.get_serializer(user, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)

    @action(detail=True, methods=['post'])
    def set_password(self, request, pk=None):
        user = self.get_object()
        
        if user != request.user and not request.user.is_staff:
            return Response(
                {'detail': 'У вас нет прав для изменения этого пароля.'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        password = request.data.get('password')
        if not password:
            return Response(
                {'password': ['Это поле обязательно.']},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        user.set_password(password)
        user.save()
        return Response({'message': 'Пароль успешно изменен'})


class AuthorViewSet(viewsets.ModelViewSet):
    queryset = Author.objects.all()
    serializer_class = AuthorSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    filter_backends = [filters.SearchFilter]
    search_fields = ['user__username', 'user__email', 'description']

    @action(detail=True, methods=['get'])
    def news(self, request, pk=None):
        author = self.get_object()
        from apps.news.models import News  # Импортируем здесь, чтобы избежать циклического импорта
        news_items = News.objects.filter(
            author=author,
            is_published=True
        ).order_by('-published_at')
        
        from apps.news.serializers import NewsSerializer
        page = self.paginate_queryset(news_items)
        if page is not None:
            serializer = NewsSerializer(page, many=True)
            return self.get_paginated_response(serializer.data)
            
        serializer = NewsSerializer(news_items, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def become_author(self, request):
        user = request.user
        
        if hasattr(user, 'author_profile'):
            return Response(
                {'detail': 'Вы уже являетесь автором.'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        author = Author.objects.create(
            user=user,
            description=request.data.get('description', '')
        )
        
        serializer = self.get_serializer(author)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

def author_list(request):
    all_authors = Author.objects.filter(user__is_active=True).order_by('user__username')

    if request.headers.get('Accept') == 'application/json':
        serializer = AuthorSerializer(all_authors, many=True)
        return JsonResponse(serializer.data, safe=False)

    context = {
        'authors': all_authors,
        'title': 'Список Авторов'
    }
    return render(request, 'author_list.html', context)


def author_detail(request, username):
    user_profile = get_object_or_404(User, username=username, is_active=True)

    try:
        author_profile = user_profile.author_profile
    except Author.DoesNotExist:
        author_profile = None

    if request.headers.get('Accept') == 'application/json':
        user_data = UserSerializer(user_profile).data
        author_data = AuthorSerializer(author_profile).data if author_profile else None
        return JsonResponse({
            'user': user_data,
            'author': author_data
        })

    context = {
        'user_data': user_profile,
        'author_data': author_profile,
        'title': f'Профиль: {user_profile.username}'
    }
    return render(request, 'author_detail.html', context)