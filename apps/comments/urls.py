from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

app_name = 'comments'

router = DefaultRouter()
router.register(r'api/comments', views.CommentViewSet, basename='comment')

urlpatterns = [
    path('news/<int:news_id>/comments/', views.comment_list, name='comment_list'),
    path('comments/<int:comment_id>/', views.comment_detail, name='comment_detail'),
    
    path('', include(router.urls)),
]