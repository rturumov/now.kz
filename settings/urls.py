from django.contrib import admin
from django.urls import path, include
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from apps.news.views import home_page

urlpatterns = [
    path('', home_page, name='home'),

    path('api/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),

    path('news/', include('apps.news.urls', namespace='news')),
    path('accounts/', include('apps.accounts.urls', namespace='accounts')),
    path('admin/', admin.site.urls),
]

