from django.shortcuts import render, get_object_or_404
from .models import Author, User


def author_list(request):
    all_authors = Author.objects.filter(user__is_active=True).order_by('user__username')
    context = {
        'authors': all_authors,
        'title': 'Список Авторов'
    }
    return render(request, 'author_list.html', context)


def author_detail(request, username):
    user_profile = get_object_or_404(User, username=username, is_active=True)

    try:
        author_profile = user_profile.author_profile
    except Author.DoesNotExist:
        author_profile = None

    context = {
        'user_data': user_profile,
        'author_data': author_profile,
        'title': f'Профиль: {user_profile.username}'
    }
    return render(request, 'author_detail.html', context)
