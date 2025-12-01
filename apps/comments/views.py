from django.shortcuts import render, get_object_or_404
from .models import Comment
from .serializers import CommentSerializer
from django.http import JsonResponse
from apps.news.models import News

def comment_list(request, news_id):
    news_item = get_object_or_404(News, id=news_id)
    comments = Comment.objects.filter(news=news_item, parent__isnull=True)

    # Если запрос JSON, вернуть сериализованные данные
    if request.headers.get('Accept') == 'application/json':
        serializer = CommentSerializer(comments, many=True)
        return JsonResponse(serializer.data, safe=False)

    # Для обычного рендера в HTML
    context = {
        'news': news_item,
        'comments': comments,
        'title': f'Комментарии к новости: {news_item.title}'
    }
    return render(request, 'comment_list.html', context)


def comment_detail(request, comment_id):
    comment = get_object_or_404(Comment, id=comment_id)

    if request.headers.get('Accept') == 'application/json':
        serializer = CommentSerializer(comment)
        return JsonResponse(serializer.data, safe=False)

    context = {
        'comment': comment,
        'title': f'Комментарий пользователя: {comment.user.username}'
    }
    return render(request, 'comment_detail.html', context)
