from django.db import models
from django.contrib.auth.models import User
# Create your models here.
class Room(models.Model):
    member = models.JSONField(default={})
    class Meta:
        db_table = 'Msg_room'

class Msg(models.Model):
    room = models.ForeignKey(Room, on_delete=models.CASCADE)
    receiver_id = models.IntegerField()
    message = models.CharField(max_length=1200)
    date = models.DateTimeField(auto_now_add=True)
    is_read = models.BooleanField(default=False)

    class Meta:
        db_table = 'Msg'

#chat model migrate 할 때 Meta의 app_label부분 주석처리 상태에서 makemigrations,
#python manage.py migrate chat --database=chatting 실행,
#이후 python manage.py migrate --fake
#모든 migrate 끝나고 app_label 주석 해제