import pytest
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient

from apps.comments.models import Comment
from apps.news.models import News, Category
from apps.accounts.models import User, Author

@pytest.fixture
def api_client():
    return APIClient()


@pytest.fixture
def user(db):
    user = User.objects.create_user(
        email="user@test.com",
        password="password123",
    )
    Author.objects.create(user=user)
    return user


@pytest.fixture
def another_user(db):
    user = User.objects.create_user(
        email="another@test.com",
        password="password123",
    )
    Author.objects.create(user=user)
    return user


@pytest.fixture
def category(db):
    return Category.objects.create(name="General")


@pytest.fixture
def news(db, user, category):
    return News.objects.create(
        title="News",
        content="Content",
        category=category,
        author=user.author_profile,
    )


@pytest.fixture
def comment(db, user, news):
    return Comment.objects.create(
        user=user,
        news=news,
        text="Test comment",
    )

# POST /api/comments/

@pytest.mark.django_db
def test_create_comment_good(api_client, user, news):
    # GOOD: Авторизованный пользователь может создать комментарий
    api_client.force_authenticate(user)
    url = reverse("comments:comment-list")

    response = api_client.post(
        url,
        {"news": news.id, "text": "New comment"},
    )

    assert response.status_code == status.HTTP_201_CREATED


@pytest.mark.django_db
def test_create_comment_bad_not_authenticated(api_client, news):
    # BAD: Неавторизованный пользователь
    url = reverse("comments:comment-list")
    response = api_client.post(
        url,
        {"news": news.id, "text": "X"},
    )

    assert response.status_code == status.HTTP_401_UNAUTHORIZED


@pytest.mark.django_db
def test_create_comment_bad_empty_text(api_client, user, news):
    # BAD: Пустой текст
    api_client.force_authenticate(user)
    url = reverse("comments:comment-list")

    response = api_client.post(
        url,
        {"news": news.id, "text": ""},
    )

    assert response.status_code == status.HTTP_400_BAD_REQUEST


@pytest.mark.django_db
def test_create_comment_bad_invalid_news(api_client, user):
    # BAD: News не существует
    api_client.force_authenticate(user)
    url = reverse("comments:comment-list")

    response = api_client.post(
        url,
        {"news": 9999, "text": "Text"},
    )

    assert response.status_code == status.HTTP_400_BAD_REQUEST

# DELETE /api/comments/{id}/

@pytest.mark.django_db
def test_delete_comment_good(api_client, user, comment):
    # GOOD: Владелец может удалить комментарий
    api_client.force_authenticate(user)
    url = reverse("comments:comment-detail", args=[comment.id])

    response = api_client.delete(url)

    assert response.status_code == status.HTTP_204_NO_CONTENT


@pytest.mark.django_db
def test_delete_comment_bad_not_owner(api_client, another_user, comment):
    # BAD: Не владелец комментария
    api_client.force_authenticate(another_user)
    url = reverse("comments:comment-detail", args=[comment.id])

    response = api_client.delete(url)

    assert response.status_code == status.HTTP_403_FORBIDDEN


@pytest.mark.django_db
def test_delete_comment_bad_not_authenticated(api_client, comment):
    # BAD: Неавторизованный пользователь
    url = reverse("comments:comment-detail", args=[comment.id])
    response = api_client.delete(url)

    assert response.status_code == status.HTTP_401_UNAUTHORIZED


@pytest.mark.django_db
def test_delete_comment_bad_not_found(api_client, user):
    # BAD: Комментарий не существует
    api_client.force_authenticate(user)
    url = reverse("comments:comment-detail", args=[9999])

    response = api_client.delete(url)

    assert response.status_code == status.HTTP_404_NOT_FOUND