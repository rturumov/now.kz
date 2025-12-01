from django.urls import path
from . import views

app_name = 'news'

urlpatterns = [
    path('', views.news_list, name='news_list'),

    path('categories/', views.category_list, name='category_list'),

    path('category/<int:category_id>/', views.news_by_category, name='news_by_category'),

    path('<int:news_id>/', views.news_detail, name='news_detail'),
]
