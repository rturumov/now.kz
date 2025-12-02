from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

app_name = 'news'

router = DefaultRouter()
router.register(r'api/categories', views.CategoryViewSet, basename='category')
router.register(r'api/news', views.NewsViewSet, basename='news')

urlpatterns = [
    path('', views.news_list, name='news_list'),
    path('categories/', views.category_list, name='category_list'),
    path('category/<int:category_id>/', views.news_by_category, name='news_by_category'),
    path('<int:news_id>/', views.news_detail, name='news_detail'),
    path('home/', views.home_page, name='home'),
    
    path('', include(router.urls)),
]