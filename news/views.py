from django.shortcuts import render, get_object_or_404
from .models import News, Category
from django.shortcuts import render


def news_list(request):
    all_news = News.objects.filter(is_published=True).order_by('-published_at')
    context = {
        'news': all_news,
        'title': 'Все Новости'
    }
    return render(request, 'news_list.html', context)


def news_detail(request, slug):
    news_item = get_object_or_404(News, slug=slug, is_published=True)
    context = {
        'news': news_item,
        'title': news_item.title
    }
    return render(request, 'news_detail.html', context)

def news_by_category(request, category_slug):
    category = get_object_or_404(Category, slug=category_slug)

    news_items = News.objects.filter(category=category, is_published=True).order_by('-published_at')

    context = {
        'category': category,
        'news': news_items,
        'title': f'Новости по категории: {category.name}'
    }
    return render(request, 'news_by_category.html', context)


from django.db.models import Count, Q



def home_page(request):
    return render(request, 'home.html', {'title': 'Главная Страница'})

def category_list(request):
    all_categories = Category.objects.annotate(
        published_news_count=Count(
            'news',
            filter=Q(news__is_published=True)
        )
    ).order_by('name')

    context = {
        'categories': all_categories,
        'title': 'Все Категории'
    }
    return render(request, 'category_list.html', context)
