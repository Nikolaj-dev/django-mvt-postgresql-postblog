from django.contrib import admin
from .models import Post, PostLike, PostComment


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


class PostCommentAdmin(admin.ModelAdmin):
    list_display = (
        'who_commented',
        'for_post',
        'comment',
        'created_time',
    )
    list_filter = (
        'who_commented',
        'for_post',
        'comment',
        'created_time',
    )
    search_fields = (
        'who_commented',
        'for_post',
    )


admin.site.register(Post, PostAdmin)
admin.site.register(PostLike, PostLikeAdmin)
admin.site.register(PostComment, PostCommentAdmin)
