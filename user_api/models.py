from django.db import models
from django.conf import settings
# Create your models here.

class Profile(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    real_name = models.CharField(max_length=10)
    type = models.SmallIntegerField(default=0)
    class_num = models.CharField(max_length=100)
    profile_image = models.ImageField(null = True)

class Tag(models.Model):
    tag = models.CharField(max_length=50)
    count = models.IntegerField(default=1)

class Tagging(models.Model):
    profile = models.ForeignKey('Profile', related_name='tagging', on_delete=models.CASCADE)
    tag = models.ForeignKey('Tag', related_name='tagging', on_delete=models.DO_NOTHING)