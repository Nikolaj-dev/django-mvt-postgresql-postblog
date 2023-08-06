from .models import Post, Profile
from django.db.models.signals import pre_delete, pre_save
from django.dispatch import receiver
import os


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
