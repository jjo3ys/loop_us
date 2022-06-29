from django.db import models
from post_api.models import Post
from user_api.models import Profile
# Create your models here.
class Group(models.Model):
    group_name = models.CharField(max_length=50, unique=True)
    
    class Meta:
        db_table = "Group"

class Tag(models.Model):
    tag = models.CharField(max_length=50, unique=True)
    count = models.IntegerField(default=1)
    monthly_count = models.JSONField(default={})
    group = models.ForeignKey(Group, related_name='tag', default=10, on_delete=models.DO_NOTHING)
    
    class Meta:
        db_table = "Tag"

class Post_Tag(models.Model):
    tag = models.ForeignKey('Tag', related_name='tags', on_delete=models.DO_NOTHING)
    post = models.ForeignKey(Post, related_name='post_tag', on_delete=models.CASCADE)

    class Meta:
        db_table = "Post_tag"