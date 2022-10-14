from django.db import models
from tag.models import Group

class News(models.Model):
    urls = models.TextField()
    group = models.ForeignKey(Group, related_name='group_news', on_delete=models.DO_NOTHING)
    corp = models.TextField(default=None, null=True)

    class Meta:
        db_table = "News"

class Brunch(models.Model):
    urls = models.TextField()
    group = models.ForeignKey(Group, related_name='group_brunch', on_delete=models.DO_NOTHING)
    writer = models.CharField(max_length=10)
    profile = models.ImageField(null=True, upload_to='brunch/')

    class Meta:
        db_table = "Brunch"

class Youtube(models.Model):
    urls = models.TextField()
    group = models.ForeignKey(Group, related_name='group_youtube', on_delete=models.DO_NOTHING)

    class Meta:
        db_table = "Youtube"
# Create your models here.
