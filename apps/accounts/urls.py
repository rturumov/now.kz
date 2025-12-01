from django.urls import path
from . import views

app_name = 'accounts'

urlpatterns = [
    path('authors/', views.author_list, name='author_list'),
    path('author/<str:username>/', views.author_detail, name='author_detail'),
]
