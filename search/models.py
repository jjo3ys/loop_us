from django.db import models
from django.conf import settings

# Create your models here.
class Log(models.Model):
    user_id = models.PositiveBigIntegerField()
    query = models.TextField()
    type = models.PositiveSmallIntegerField(default=0)
    date = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        app_label = 'log'
        db_table = 'Search_Log'

class InterestTag(models.Model):
    tag_list = models.JSONField(default=dict)
    user_id = models.PositiveBigIntegerField()

    class Meta:
        app_label = 'log'
        db_table = "Interest_tag"

# class Connect_log(models.Model):
#     date = models.DateField(auto_now_add=True)
#     user_id = models.PositiveIntegerField()

#     class Meta:
#         app_label = 'log'
#         db_table = 'Connection_log'

#chat model migrate 할 때 Meta의 app_label부분 주석처리 상태에서 makemigrations,
#python manage.py migrate search --database=log 실행,
#이후 python manage.py migrate --fake
#모든 migrate 끝나고 app_label 주석 해제