from django import template
from django.shortcuts import get_object_or_404
from django.utils.text import Truncator
from django.core.cache import cache
from ..models import Post, PostLike, PostComment

register = template.Library()


@register.simple_tag(takes_context=True)
# check if like on the post exists, if it does, then check if it is liked or not
def post_like(context, post_id):
    user = context["request"].user
    try:
        like = PostLike.objects.get(for_post_id=post_id, who_liked_id=user.id)
        return like
    except:
        return None


@register.simple_tag()
def count_comments(slug: str) -> int:
    post = cache.get("detailed_post %s" % (str(slug),))
    if not post:
        post = get_object_or_404(Post, slug=slug)
        cache.set("detailed_post %s" % (str(slug),), post, timeout=15)
    comments = PostComment.objects.filter(
        for_post=post,
    ).count()
    return int(comments)


@register.simple_tag()
def count_likes(slug: int) -> int:
    post = cache.get("detailed_post %s" % (str(slug),))
    if not post:
        post = get_object_or_404(Post, slug=slug)
        cache.set("detailed_post %s" % (str(slug),), post, timeout=15)
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


@register.filter
def cut_sentences(value, num_sentences):
    truncator = Truncator(value)
    return truncator.words(num_sentences, truncate=' ...')