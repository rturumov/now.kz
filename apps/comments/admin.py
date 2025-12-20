from django.contrib import admin
from .models import Comment

@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'news', 'parent', 'deleted_at', 'created_at')
    search_fields = ('user__username', 'news__title', 'text')
    list_filter = ('created_at',)
    readonly_fields = ('created_at', 'updated_at')