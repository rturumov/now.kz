from django.utils import timezone
import pytest
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient

from apps.news.models import News, Category
from apps.accounts.models import User, Author

@pytest.fixture
def api_client():
    return APIClient()

@pytest.fixture
def author_user(db):
    user = User.objects.create_user(
        email="author@test.com",
        password="password123",
    )
    Author.objects.create(user=user)
    return user


@pytest.fixture
def another_user(db):
    return User.objects.create_user(
        email="user@test.com",
        password="password123",
    )

@pytest.fixture
def category(db):
    return Category.objects.create(name="Technology")

@pytest.fixture
def news(db, author_user, category):
    return News.objects.create(
        title="Test news",
        content="Content",
        category=category,
        author=author_user.author_profile,
        is_published=True,
        published_at=timezone.now() - timezone.timedelta(seconds=1),
        deleted_at=None,
    )

# GET /api/news/

@pytest.mark.django_db
def test_news_list_good(api_client):
    # GOOD: Любой пользователь может получить список новостей
    url = reverse("news:news-list")
    response = api_client.get(url)

    assert response.status_code == status.HTTP_200_OK

    data = response.data["results"] if isinstance(response.data, dict) else response.data
    assert isinstance(data, list)

@pytest.mark.django_db
def test_news_list_bad_invalid_date_range(api_client):
    # BAD: date_from > date_to → ошибка
    url = reverse("news:news-list") + "?date_from=2025-01-10&date_to=2024-01-01"
    response = api_client.get(url)

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert "date_from" in response.data

@pytest.mark.django_db
def test_news_list_bad_invalid_bool(api_client):
    # BAD: is_published должен быть boolean
    url = reverse("news:news-list") + "?is_published=not_bool"
    response = api_client.get(url)

    assert response.status_code == status.HTTP_400_BAD_REQUEST


@pytest.mark.django_db
def test_news_list_bad_unknown_category(api_client):
    # BAD: Неизвестная категория → пустой список
    url = reverse("news:news-list") + "?category_id=9999"
    response = api_client.get(url)

    assert response.status_code == status.HTTP_200_OK
    assert response.data == []

# POST /api/news/

@pytest.mark.django_db
def test_create_news_good(api_client, author_user, category):
    # GOOD: Автор может создать новость
    api_client.force_authenticate(author_user)
    url = reverse("news:news-list")

    response = api_client.post(
        url,
        {
            "title": "New news",
            "content": "Text",
            "category": category.id,
        },
    )

    assert response.status_code == status.HTTP_201_CREATED


@pytest.mark.django_db
def test_create_news_bad_not_authenticated(api_client, category):
    # BAD: Неавторизованный пользователь
    url = reverse("news:news-list")
    response = api_client.post(url, {"title": "X"})

    assert response.status_code == status.HTTP_401_UNAUTHORIZED


@pytest.mark.django_db
def test_create_news_bad_not_author(api_client, another_user, category):
    # BAD: Авторизован, но не автор
    api_client.force_authenticate(another_user)
    url = reverse("news:news-list")

    response = api_client.post(
        url,
        {"title": "X", "content": "Y", "category": category.id},
    )

    assert response.status_code == status.HTTP_403_FORBIDDEN


@pytest.mark.django_db
def test_create_news_bad_empty_title(api_client, author_user, category):
    # BAD: Пустой title
    api_client.force_authenticate(author_user)
    url = reverse("news:news-list")

    response = api_client.post(
        url,
        {"title": "", "content": "Text", "category": category.id},
    )

    assert response.status_code == status.HTTP_400_BAD_REQUEST

@pytest.mark.django_db
def test_publish_news_good(api_client, author_user, news):
    # GOOD: Автор может публиковать свою новость
    api_client.force_authenticate(author_user)
    url = reverse("news:news-publish", args=[news.id])

    response = api_client.post(url)

    assert response.status_code == status.HTTP_200_OK
    assert response.data["is_published"] is True


@pytest.mark.django_db
def test_publish_news_bad_not_owner(api_client, another_user, news):
    # BAD: Пользователь не является владельцем
    api_client.force_authenticate(another_user)
    url = reverse("news:news-publish", args=[news.id])

    response = api_client.post(url)

    assert response.status_code == status.HTTP_403_FORBIDDEN


@pytest.mark.django_db
def test_publish_news_bad_not_authenticated(api_client, news):
    # BAD: Неавторизован
    url = reverse("news:news-publish", args=[news.id])
    response = api_client.post(url)

    assert response.status_code == status.HTTP_401_UNAUTHORIZED


@pytest.mark.django_db
def test_publish_news_bad_not_found(api_client, author_user):
    # BAD: Новость не существует
    api_client.force_authenticate(author_user)
    url = reverse("news:news-publish", args=[9999])

    response = api_client.post(url)

    assert response.status_code == status.HTTP_404_NOT_FOUND