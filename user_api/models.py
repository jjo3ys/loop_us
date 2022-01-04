from django.db import models
from django.conf import settings

class Profile(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, unique=True)
    real_name = models.CharField(max_length=10)
    type = models.SmallIntegerField(default=0)
    profile_image = models.ImageField(null = True)
    department = models.CharField(default='기타', max_length=15)

    class Meta:
        db_table = "Profile"

class Company_Inform(models.Model):
    profile = models.ForeignKey(Profile, on_delete=models.CASCADE, related_name='company_inform')
    corp_num = models.CharField(max_length=10)
    corp_name = models.TextField()

    class Meta:
        db_table = "Corp_inform"

class Activation(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    corp_num = models.CharField(max_length=10)
    corp_name = models.TextField()
    email = models.TextField()
    name = models.CharField(max_length=10)
    tel_num = models.TextField()
    
    class Meta:
        db_table = "Corp_active"

