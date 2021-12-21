from django.db import models
from django.conf import settings
from project_api.models import Project


# Create your models here.


class Post(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    project = models.ForeignKey(Project, related_name='post', on_delete=models.CASCADE)
    title = models.TextField(null=True)
    thumbnail = models.ImageField(null=True)
    date = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "post"
    

class Contents(models.Model):
    post = models.ForeignKey(Post, related_name='contents', on_delete=models.CASCADE)
    content = models.TextField(null=True)
    date = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "post_contents"

class ContentsImage(models.Model):
    contents = models.ForeignKey(Contents, related_name='contents_image', on_delete=models.CASCADE)
    image = models.ImageField(null=True)

    class Meta:
        db_table = "post_image"

class Like(models.Model):
    post = models.ForeignKey(Post, null=True, related_name='like', on_delete=models.CASCADE)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)

    class Meta:
        db_table = "post_like"