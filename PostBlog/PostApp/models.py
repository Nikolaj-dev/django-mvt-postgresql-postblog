from django.contrib.auth.models import User
from django.db import models


class Post(models.Model):
    title = models.CharField('Title', max_length=128, db_index=True)
    body = models.TextField()
    created_date = models.DateField(auto_now_add=True)
    author = models.ForeignKey(User, on_delete=models.CASCADE, default=None)


    def __str__(self):
        return self.title

