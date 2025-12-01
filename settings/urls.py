from django.contrib import admin
from django.urls import path, include

from apps.news.views import home_page

urlpatterns = [
    path('', home_page, name='home'),

    path('news/', include('apps.news.urls', namespace='news')),

    path('accounts/', include('apps.accounts.urls', namespace='accounts')),

    path('admin/', admin.site.urls),
]

