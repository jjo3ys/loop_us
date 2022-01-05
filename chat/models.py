from django.db import models
from django.contrib.auth.models import User
# Create your models here.
class Msg(models.Model):
    sender = models.ForeignKey(User, on_delete=models.CASCADE, related_name='sendser')
    receiver = models.ForeignKey(User, on_delete=models.CASCADE, related_name='receiver')
    message = models.CharField(max_length=1200)
    date = models.DateTimeField(auto_now_add=True)
    is_read = models.BooleanField(default=False)

    class Meta:
        db_table = 'Msg'