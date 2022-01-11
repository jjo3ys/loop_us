from django.db import models
from django.contrib.auth.models import User
# Create your models here.
class Room(models.Model):
    member = models.JSONField(default={})
    class Meta:
        app_label = "chatting"
        db_table = 'Msg_room'

class Msg(models.Model):
    room = models.ForeignKey(Room, on_delete=models.CASCADE)
    receiver_id = models.IntegerField()
    message = models.CharField(max_length=1200)
    date = models.DateTimeField(auto_now_add=True)
    is_read = models.BooleanField(default=False)

    class Meta:
        app_label = "chatting"
        db_table = 'Msg'

#chat model migrate 할 때 python manage.py migrate chat --database=chatting