import pytest
from django.urls import reverse
from rest_framework import status
from apps.news.models import News, Category
from apps.accounts.models import User, Author

@pytest.fixture
def api_client():
    from rest_framework.test import APIClient
    return APIClient()

@pytest.fixture
def user(db):
    user = User.objects.create_user(username='testuser', email='test@example.com', password='password123')
    Author.objects.create(user=user)
    return user

@pytest.fixture
def another_user(db):
    user = User.objects.create_user(username='otheruser', email='other@example.com', password='password123')
    Author.objects.create(user=user)
    return user

@pytest.fixture
def category(db):
    return Category.objects.create(name='Тестовая категория')

@pytest.fixture
def news(db, user, category):
    return News.objects.create(title='Тестовая новость', content='Текст новости', category=category, author=user.author_profile)

# Позитивные тесты
@pytest.mark.django_db
def test_list_news(api_client, news):
    url = reverse('news:news-list')
    response = api_client.get(url)
    assert response.status_code == status.HTTP_200_OK

@pytest.mark.django_db
def test_retrieve_news(api_client, news):
    url = reverse('news:news-detail', args=[news.id])
    response = api_client.get(url)
    assert response.status_code == status.HTTP_200_OK
    assert response.data['title'] == news.title

@pytest.mark.django_db
def test_create_news_authorized(api_client, user, category):
    api_client.force_authenticate(user=user)
    url = reverse('news:news-list')
    data = {'title': 'Новая новость', 'content': 'Текст новости', 'category_id': category.id}
    response = api_client.post(url, data)
    assert response.status_code == status.HTTP_201_CREATED

@pytest.mark.django_db
def test_create_news_unauthorized(api_client, category):
    url = reverse('news:news-list')
    data = {'title': 'Новая новость', 'content': 'Текст новости', 'category_id': category.id}
    response = api_client.post(url, data)
    assert response.status_code == status.HTTP_401_UNAUTHORIZED

@pytest.mark.django_db
def test_my_news(api_client, user, news):
    api_client.force_authenticate(user=user)
    url = reverse('news:news-my-news')
    response = api_client.get(url)
    assert response.status_code == status.HTTP_200_OK
    assert response.data['results'][0]['id'] == news.id

@pytest.mark.django_db
def test_list_news_by_category(api_client, category, news):
    url = reverse('news:category-news', args=[category.id])
    response = api_client.get(url)
    assert response.status_code == status.HTTP_200_OK
    assert response.data['results'][0]['category']['id'] == category.id

@pytest.mark.django_db
def test_publish_news_by_author(api_client, user, news):
    api_client.force_authenticate(user=user)
    url = reverse('news:news-publish', args=[news.id])
    response = api_client.post(url)
    assert response.status_code == status.HTTP_200_OK
    assert response.data['is_published'] is True

@pytest.mark.django_db
def test_unpublish_news_by_author(api_client, user, news):
    news.is_published = True
    news.save()
    api_client.force_authenticate(user=user)
    url = reverse('news:news-unpublish', args=[news.id])
    response = api_client.post(url)
    assert response.status_code == status.HTTP_200_OK
    assert response.data['is_published'] is False

# Негативные тесты
@pytest.mark.django_db
def test_update_news_non_author(api_client, another_user, news):
    api_client.force_authenticate(user=another_user)
    url = reverse('news:news-detail', args=[news.id])
    response = api_client.patch(url, {'title': 'Изменено'})
    assert response.status_code == status.HTTP_403_FORBIDDEN

@pytest.mark.django_db
def test_publish_news_non_author(api_client, another_user, news):
    api_client.force_authenticate(user=another_user)
    url = reverse('news:news-publish', args=[news.id])
    response = api_client.post(url)
    assert response.status_code == status.HTTP_403_FORBIDDEN

@pytest.mark.django_db
def test_unpublish_news_non_author(api_client, another_user, news):
    news.is_published = True
    news.save()
    api_client.force_authenticate(user=another_user)
    url = reverse('news:news-unpublish', args=[news.id])
    response = api_client.post(url)
    assert response.status_code == status.HTTP_403_FORBIDDEN