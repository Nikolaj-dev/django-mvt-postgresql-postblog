import os

from django.contrib.auth.models import User
from django.db import models
from django.db.models.signals import pre_delete, pre_save
from django.dispatch import receiver


class Post(models.Model):
    title = models.CharField('Title', max_length=128, db_index=True)
    body = models.TextField('Text',)
    created_date = models.DateField('Date of creation', auto_now_add=True)
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    image = models.ImageField(upload_to='posts_images/')

    def __str__(self):
        return self.title


@receiver(pre_delete, sender=Post)
def post_image_delete(sender, instance, **kwargs):
    instance.image.delete(False)


@receiver(pre_save, sender=Post)
def delete_old_file(sender, instance, **kwargs):
    if instance._state.adding and instance.pk:
        return False

    try:
        old_file = sender.objects.get(pk=instance.pk).image
    except sender.DoesNotExist:
        return False

    # comparing the new file with the old one
    file = instance.image
    if not old_file == file:
        if os.path.isfile(old_file.path):
            os.remove(old_file.path)


class PostLike(models.Model):
    who_liked = models.ForeignKey(User, on_delete=models.CASCADE)
    for_post = models.ForeignKey(Post, on_delete=models.CASCADE)
    is_liked = models.BooleanField(default=True)


class PostComment(models.Model):
    who_commented = models.ForeignKey(User, on_delete=models.CASCADE)
    for_post = models.ForeignKey(Post, on_delete=models.CASCADE)
    comment = models.TextField()
    created_time = models.DateTimeField(auto_now_add=True)


class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    profile_img = models.ImageField(upload_to='profiles_images/')
    nickname = models.CharField(max_length=64)
