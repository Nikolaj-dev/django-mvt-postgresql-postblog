from django.contrib import admin
from .models import Post, PostLike


class PostAdmin(admin.ModelAdmin):
    list_display = (
        'title',
        'body',
        'created_date',
        'image',
        'author',
    )
    list_filter = (
        'created_date',
        'author',
    )
    search_fields = (
        'title',
        'author',
    )


class PostLikeAdmin(admin.ModelAdmin):
    list_display = (
        'who_liked',
        'for_post',
    )
    list_filter = (
        'who_liked',
        'for_post',
    )
    search_fields = (
        'who_liked',
        'for_post',
    )


admin.site.register(Post, PostAdmin)
admin.site.register(PostLike, PostLikeAdmin)

