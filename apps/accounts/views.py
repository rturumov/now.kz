from django.shortcuts import render, get_object_or_404
from .models import Author, User
from .serializers import UserSerializer, AuthorSerializer
from django.http import JsonResponse

def author_list(request):
    all_authors = Author.objects.filter(user__is_active=True).order_by('user__username')

    if request.headers.get('Accept') == 'application/json':
        serializer = AuthorSerializer(all_authors, many=True)
        return JsonResponse(serializer.data, safe=False)

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

    if request.headers.get('Accept') == 'application/json':
        user_data = UserSerializer(user_profile).data
        author_data = AuthorSerializer(author_profile).data if author_profile else None
        return JsonResponse({
            'user': user_data,
            'author': author_data
        })

    context = {
        'user_data': user_profile,
        'author_data': author_profile,
        'title': f'Профиль: {user_profile.username}'
    }
    return render(request, 'author_detail.html', context)
