from django.db import models
from django.conf import settings
from django.contrib.auth.models import User


class Profile(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    real_name = models.CharField(max_length=10)
    type = models.SmallIntegerField(default=0)
    profile_image = models.ImageField(null = True, upload_to='profile_image/')
    department = models.PositiveSmallIntegerField(default=0)

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

class Banlist(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    banlist = models.JSONField(default=None, null=True)

    class Meta:
        db_table = "Ban_list"

class Report(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    type = models.SmallIntegerField(default=0)
    target_id = models.PositiveBigIntegerField()
    reason = models.CharField(max_length=100)
    date = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "Report"

class Alarm(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='alarm_user')
    alarm_from = models.ForeignKey(User, on_delete=models.CASCADE, related_name='alarm_from')
    type = models.PositiveSmallIntegerField()
    target_id = models.PositiveIntegerField()
    date = models.DateTimeField(auto_now_add=True)
    is_read = models.BooleanField(default=False)
    
    class Meta:
        db_table = "Alarm"