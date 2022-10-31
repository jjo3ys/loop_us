from django.db import models
from django.conf import settings

from post_api.models import Post

# Create your models here.
class PostingRanking(models.Model):
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='ranked_post')
    group = models.PositiveSmallIntegerField(default=16)
    score = models.SmallIntegerField(default=0)

    class Meta:
        db_table = 'PostingRanking'
        
class HotUser(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, null=True)
    group = models.PositiveSmallIntegerField(default=16)
    like_count = models.PositiveIntegerField(default=0)
    
    class Meta:
        db_table = 'HotUser'