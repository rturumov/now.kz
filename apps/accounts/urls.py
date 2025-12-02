from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

app_name = 'accounts'

router = DefaultRouter()
router.register(r'api/users', views.UserViewSet, basename='user')
router.register(r'api/authors', views.AuthorViewSet, basename='author')

urlpatterns = [
    path('authors/', views.author_list, name='author_list'),
    path('author/<str:username>/', views.author_detail, name='author_detail'),
    
    path('', include(router.urls)),
]