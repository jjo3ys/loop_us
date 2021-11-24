from django.db import models
from django.contrib.auth.models import User

class Loopship(models.Model):
    first = models.ForeignKey(User, on_delete=models.CASCADE, related_name='user')
    second = models.ForeignKey(User, on_delete=models.CASCADE, related_name='loop')
    active = models.BooleanField(default=False)

    class Meta:
        db_table = "loopship"