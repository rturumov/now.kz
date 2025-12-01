from django.urls import path
from . import views

app_name = 'comments'

urlpatterns = [
    path('news/<int:news_id>/comments/', views.comment_list, name='comment_list'),
    path('comments/<int:comment_id>/', views.comment_detail, name='comment_detail'),
]
