from django.db import models
from django.conf import settings
from django.contrib.auth.models import User

def file_upload_path(instance, filename):
    return 'post_file/{}/{}'.format(instance.post.user_id, filename)

# Career
class Career(models.Model):
    career_name = models.CharField(max_length=50)
    post_update_date = models.DateTimeField(null=True, default=None)
    group = models.PositiveSmallIntegerField(default=15)
    thumbnail = models.PositiveBigIntegerField(null=True, default=0)
    is_public = models.BooleanField(default=False)
    tag_company = models.BooleanField(default=False)
    class Meta:
        db_table = 'Career'

class CareerUser(models.Model):
    career = models.ForeignKey(Career, on_delete=models.CASCADE, related_name='career')
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='member')
    post_count = models.PositiveSmallIntegerField(default=0)
    order = models.PositiveSmallIntegerField(default=None, null=True)
    is_manager = models.BooleanField(default=1)

    class Meta:
        db_table = 'CareerUser'


# Post
class Post(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    career = models.ForeignKey(Career, related_name='post', on_delete=models.CASCADE)
    contents = models.TextField(null=True)
    date = models.DateTimeField(auto_now_add=True)
    like_count = models.SmallIntegerField(default=0)
    view_count = models.PositiveBigIntegerField(default=0)

    class Meta:
        db_table = "Posting"
        
class PostingRanking(models.Model):
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='ranked_post')
    group = models.PositiveSmallIntegerField(default=15)
    score = models.SmallIntegerField(default=0)

    class Meta:
        db_table = 'PostingRanking'
        
class PostLink(models.Model):
    post = models.ForeignKey(Post, related_name='contents_link', on_delete=models.CASCADE)
    link = models.TextField()

    class Meta:
        db_table = "Post_link"

class PostImage(models.Model):
    post = models.ForeignKey(Post, related_name='contents_image', on_delete=models.CASCADE)
    image = models.ImageField(null=True, upload_to='post/')

    class Meta:
        db_table = "Post_image"
        
def file_upload_path(instance, filename):
    return 'post_file/{}/{}'.format(instance.post.user_id, filename)

class PostFile(models.Model):
    post = models.ForeignKey(Post, related_name='contents_file', on_delete=models.CASCADE)
    file = models.FileField(upload_to=file_upload_path)
    
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

class CorpLike(models.Model):
    post = models.ForeignKey(Post, null=True, related_name='corp_like', on_delete=models.CASCADE)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)

    class Meta:
        db_table = "Corp_like"

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
        
#tag
class Group(models.Model):
    group_name = models.CharField(max_length=50, unique=True)
    monthly_count = models.JSONField(default=dict)
    
    class Meta:
        db_table = "Group"

class Tag(models.Model):
    tag = models.CharField(max_length=50, unique=True)
    count = models.IntegerField(default=1)
    monthly_count = models.JSONField(default=dict)
    group = models.ForeignKey(Group, related_name='tag', default=15, on_delete=models.DO_NOTHING)
    
    class Meta:
        db_table = "Tag"

class Post_Tag(models.Model):
    tag = models.ForeignKey('Tag', related_name='tags', on_delete=models.DO_NOTHING)
    post = models.ForeignKey(Post, related_name='post_tag', on_delete=models.CASCADE)
    class Meta:
        db_table = "Post_tag"