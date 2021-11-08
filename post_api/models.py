from django.db import models
from django.conf import settings
from project_api.models import Project


# Create your models here.


class Posting(models.Model):
    author = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    project = models.ForeignKey(Project, on_delete=models.CASCADE)
    # sequance = models.CharField(max_length=100)
    thumbnail = models.ImageField(null=True)
    title = models.TextField(null=True)
    date = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "posting"

class PostingContents(models.Model):
    posting = models.ForeignKey('Posting', related_name='posting_content', on_delete=models.CASCADE)
    # sequance = models.CharField(max_length=100)
    contentType = models.CharField(max_length=100)
    content = models.TextField(null=True)
    date = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "posting_contents"