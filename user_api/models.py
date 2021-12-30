from django.db import models
from django.conf import settings
from .department import DEPARTMENT
# Create your models here.
DEPARTMENT_CHOICES = (DEPARTMENT.items())

class Profile(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, unique=True)
    real_name = models.CharField(max_length=10)
    type = models.SmallIntegerField(default=0)
    profile_image = models.ImageField(null = True)
    department = models.CharField(default='기타', max_length=15)

