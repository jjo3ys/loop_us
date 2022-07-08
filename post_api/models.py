from django.db import models
from django.conf import settings
from project_api.models import Project
from user_api.models import User
# Create your models here.


class Post(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    project = models.ForeignKey(Project, related_name='post', on_delete=models.CASCADE)
    contents = models.TextField(null=True)
    date = models.DateTimeField(auto_now_add=True)
    like_count = models.SmallIntegerField(default=0)
    view_count = models.PositiveBigIntegerField(default=0)

    class Meta:
        db_table = "Posting"

class PostLink(models.Model):
    post = models.ForeignKey(Post, related_name='contents_link', on_delete=models.CASCADE)
    link = models.TextField()

    class Meta:
        db_table = "Post_link"

class PostImage(models.Model):
    post = models.ForeignKey(Post, related_name='contents_image', on_delete=models.CASCADE)
    image = models.ImageField(null=True, upload_to='post/image/%Y%m%d/')

    class Meta:
        db_table = "Post_image"
    
class Comment(models.Model):
    post = models.ForeignKey(Post, related_name='comments', on_delete=models.CASCADE)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    content = models.TextField()
    date = models.DateTimeField(auto_now_add=True)
    like_count = models.SmallIntegerField(default=0)
    
    class Meta:
        db_table = "Post_comment"

class Cocomment(models.Model):
    comment = models.ForeignKey(Comment, related_name='cocomments', on_delete=models.CASCADE)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    content = models.TextField()
    date = models.DateTimeField(auto_now_add=True)
    like_count = models.SmallIntegerField(default=0)
    tagged = models.ForeignKey(User, default=None, null=True, related_name='tagged_user', on_delete=models.DO_NOTHING)
    
    class Meta:
        db_table = "Post_cocomment"

class Like(models.Model):
    post = models.ForeignKey(Post, null=True, related_name='post_like', on_delete=models.CASCADE)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)

    class Meta:
        db_table = "Post_like"

class CommentLike(models.Model):
    comment = models.ForeignKey(Comment, null=True, related_name='comment_like', on_delete=models.CASCADE)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)

    class Meta:
        db_table = "Comment_like"

class CocommentLike(models.Model):
    cocomment = models.ForeignKey(Cocomment, null=True, related_name='cocomment_like', on_delete=models.CASCADE)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)

    class Meta:
        db_table = "Cocomment_like"

class BookMark(models.Model):
    post = models.ForeignKey(Post, related_name='bookmark', on_delete=models.CASCADE)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)

    class Meta:
        db_table = "Post_bookmark"