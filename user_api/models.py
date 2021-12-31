from django.db import models
from django.conf import settings

class Profile(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, unique=True)
    real_name = models.CharField(max_length=10)
    type = models.SmallIntegerField(default=0)
    profile_image = models.ImageField(null = True)
    department = models.CharField(default='기타', max_length=15)

    class Meta:
        db_table = "profile"

class Company_Inform(models.Model):
    profile = models.ForeignKey(Profile, on_delete=models.CASCADE)
    corp_num = models.CharField(max_length=10)
    corp_name = models.TextField()
    tel_num = models.CharField(max_length=13)

