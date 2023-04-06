from django import template

from ..models import Post, PostLike, PostComment

register = template.Library()


@register.simple_tag(takes_context=True)
def posts_(context, post_id):
    user = context["request"].user
    try:
        like = PostLike.objects.get(for_post_id=post_id, who_liked_id=user.id)
        return like
    except:
        return None


@register.simple_tag()
def count_comments(post_id):
    post = Post.objects.get(pk=post_id)
    comments = PostComment.objects.filter(
        for_post=post,
    ).count()
    return int(comments)


@register.simple_tag()
def count_likes(post_id):
    post = Post.objects.get(pk=post_id)
    likes = PostLike.objects.filter(
        for_post=post,
        is_liked=True,
    ).count()
    return int(likes)


@register.simple_tag()
def all_comments(post_id):
    post = Post.objects.get(pk=post_id)
    comments = PostComment.objects.filter(
        for_post=post,
    ).order_by('-created_time')
    return comments

