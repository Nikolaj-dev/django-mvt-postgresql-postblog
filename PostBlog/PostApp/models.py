import os
from PIL import Image
from django.contrib.auth.models import User
from django.db import models
from django.db.models.signals import pre_delete, pre_save
from django.dispatch import receiver
from django.utils.text import slugify


class Post(models.Model):
    title = models.CharField('Title', max_length=128, db_index=True)
    body = models.TextField('Text')
    created_date = models.DateField('Date of creation', auto_now_add=True)
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    image = models.ImageField(upload_to='posts_images/')
    slug = models.SlugField(
        null=False,
        blank=True,
        unique=True,
    )

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        if not self.slug:

            q = Post.objects.values_list('id', flat=True).order_by('-id')[:1]
            if len(q):
                self.number = str(self.id) if self.id else str(
                    int(q.get()) + 1)
            else:
                self.number = 1

            self.slug = slugify(
                self.title + '-' + str(self.number)
            )
        super(Post, self).save(*args, **kwargs)


@receiver(pre_delete, sender=Post)
def post_image_delete(sender, instance, **kwargs):
    instance.image.delete(False)


@receiver(pre_save, sender=Post)
def delete_old_post_image(sender, instance, **kwargs):
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

    def __str__(self):
        return str(f"{self.who_liked} liked {self.for_post}")


class PostComment(models.Model):
    who_commented = models.ForeignKey(User, on_delete=models.CASCADE)
    for_post = models.ForeignKey(Post, on_delete=models.CASCADE)
    comment = models.TextField(max_length=5000)
    created_time = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return str(f"{self.who_commented} commented {self.for_post}")


class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    profile_img = models.ImageField(upload_to='profiles_images/')
    nickname = models.CharField(max_length=64, unique=True)
    about = models.TextField(max_length=5000, null=True, blank=True)

    def __str__(self):
        return str(self.nickname)

    def save(
        self, force_insert=False, force_update=False, using=None, update_fields=None
    ):
        super().save()
        img = Image.open(self.profile_img.path)  # Open image using self

        if img.height > 480 or img.width > 480:
            new_img = (480, 480)
            img.thumbnail(new_img)
            img.save(self.profile_img.path)  # saving image at the same path


@receiver(pre_delete, sender=Profile)
def profile_image_delete(sender, instance, **kwargs):
    instance.profile_img.delete(False)


@receiver(pre_save, sender=Profile)
def delete_old_profile_image(sender, instance, **kwargs):
    if instance._state.adding and instance.pk:
        return False
    try:
        old_file = sender.objects.get(pk=instance.pk).profile_img
    except sender.DoesNotExist:
        return False

    # comparing the new file with the old one
    file = instance.profile_img
    if not old_file == file:
        if os.path.isfile(old_file.path):
            os.remove(old_file.path)


class Follower(models.Model):
    who_followed = models.ForeignKey(Profile, on_delete=models.CASCADE, related_name='who_followed')
    who_follow = models.ForeignKey(Profile, on_delete=models.CASCADE, related_name='who_follow')

    def __str__(self):
        return str(f'{self.who_follow} following {self.who_followed}')
