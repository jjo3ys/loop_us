from django.db import models
from django.contrib.auth.models import User
from django.conf import settings

class Request(models.Model):
    From = models.ForeignKey(User, on_delete=models.CASCADE, related_name='From')
    To = models.ForeignKey(User, on_delete=models.CASCADE, related_name='To')
    is_active = models.BooleanField(default=False)

    class Meta:
        db_table = "Loop_request"

class Loopship(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='user')
    friend = models.ForeignKey(User, on_delete=models.CASCADE, related_name='loop')

    class Meta:
        db_table = "Loopship"