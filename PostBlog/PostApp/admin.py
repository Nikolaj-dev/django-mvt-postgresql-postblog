from django.contrib import admin
from .models import Post


class PostAdmin(admin.ModelAdmin):
    list_display = (
        'title',
        'body',
        'created_date',
    )
    list_filter = (
        'created_date',
    )
    search_fields = (
        'title',
    )


admin.site.register(Post, PostAdmin)

