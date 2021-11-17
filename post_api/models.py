from django.db import models
from django.conf import settings
from project_api.models import Project


# Create your models here.


class Posting(models.Model):
    author = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    project = models.ForeignKey(Project, on_delete=models.CASCADE)
    # sequance = models.CharField(max_length=100)
    title = models.TextField(null=True)
    thumbnail = models.ImageField(null=True)
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

class PostingContentsImage(models.Model):
    author = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    PostingContents = models.ForeignKey('PostingContents', related_name='posting_image', on_delete=models.CASCADE)
    image = models.ImageField(null=True)

class Like(models.Model):
    posting = models.ForeignKey(Posting, null=True, related_name='like', on_delete=models.CASCADE)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
