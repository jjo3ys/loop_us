from django.db import models
from post_api.models import Post

# Create your models here.
class PostingRanking(models.Model):
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='ranked_post')
    group = models.PositiveSmallIntegerField(default=10)
    score = models.SmallIntegerField(default=0)

    class Meta:
        db_table = 'PostingRanking'