from django.db import models
from django.conf import settings

# Create your models here.
class Log(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.DO_NOTHING)
    query = models.TextField()
    date = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'Log'