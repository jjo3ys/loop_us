from turtle import ondrag
from django.db import models
from tag.models import Group

class News(models.Model):
    urls = models.TextField()
    group = models.ForeignKey(Group, related_name='group_news', on_delete=models.DO_NOTHING)

    class Meta:
        db_table = "News"

class Insta(models.Model):
    content = models.TextField()
    date = models.DateTimeField()
    group = models.ForeignKey(Group, related_name='group_insta', on_delete=models.DO_NOTHING)

    class Meta:
        db_table = "InstaFeed"

class Youtube(models.Model):
    urls = models.TextField()
    group = models.ForeignKey(Group, related_name='group_youtube', on_delete=models.DO_NOTHING)

    class Meata:
        db_table = "Youtube"
# Create your models here.
