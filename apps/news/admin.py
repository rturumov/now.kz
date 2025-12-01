from django.contrib import admin
from .models import News, Category

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'is_deleted', 'created_at', 'updated_at')
    search_fields = ('name',)


@admin.register(News)
class NewsAdmin(admin.ModelAdmin):
    list_display = ('id', 'title', 'category', 'author', 'is_published', 'is_deleted', 'published_at')
    list_filter = ('is_published', 'category', 'author')
    search_fields = ('title', 'content')
    readonly_fields = ('created_at', 'updated_at', 'published_at')