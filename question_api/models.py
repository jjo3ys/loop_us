from django.db import models
from django.conf import settings

# Create your models here.

class Question(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    content = models.TextField(null=True)
    adopt = models.BooleanField(null=False)
    date = models.DateField(null=True)


class Answer(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    content = models.TextField(null=True)
    adopt = models.BooleanField(null=False)
    date = models.DateField(null=True)

