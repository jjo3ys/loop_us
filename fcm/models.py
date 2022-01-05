from django.db import models
from django.conf import settings

# Create your models here.

class FcmToken(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    token = models.TextField()

    class Meta:
        db_table = 'FcmToken'