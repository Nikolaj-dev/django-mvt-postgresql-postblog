from django import template

from ..models import Post, PostLike

register = template.Library()


@register.simple_tag(takes_context=True)
def posts_(context, post_id):
    user = context["request"].user
    try:
        like = PostLike.objects.get(for_post_id=post_id, who_liked_id=user.id)
        return like
    except:
        return None

