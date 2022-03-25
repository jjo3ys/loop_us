from django.db import models
from post_api.models import Post
from user_api.models import Profile
# Create your models here.
class Tag(models.Model):
    tag = models.CharField(max_length=50, unique=True)
    count = models.IntegerField(default=1)

    class Meta:
        db_table = "Tag"

class Post_Tag(models.Model):
    tag = models.ForeignKey('Tag', related_name='post_tag', on_delete=models.DO_NOTHING)
    post = models.ForeignKey(Post, related_name='post_tag', on_delete=models.CASCADE)

    class Meta:
        db_table = "Post_tag"

class Profile_Tag(models.Model):
    tag = models.ForeignKey('Tag', related_name='profile_tag', on_delete=models.DO_NOTHING)
    profile = models.ForeignKey(Profile, related_name='profile_tag', on_delete=models.CASCADE)

    class Meta:
        db_table = 'Prof_tag'