from django.db import models
from django.conf import settings

# Create your models here.
class Log(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.DO_NOTHING)
    query = models.TextField()
    date = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        app_label = 'log'
        db_table = 'Search_Log'

class Connect_log(models.Model):
    date = models.DateField(auto_now_add=True, primary_key=True)
    id = models.PositiveIntegerField()

    class Meta:
        app_label = 'log'
        db_table = 'Connection_log'

#chat model migrate 할 때 Meta의 app_label부분 주석처리 상태에서 makemigrations,
#python manage.py migrate chat --database=log 실행,
#이후 python manage.py migrate --fake
#모든 migrate 끝나고 app_label 주석 해제