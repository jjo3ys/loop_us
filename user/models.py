from django.db import models
from django.conf import settings
from django.contrib.auth.models import User

from career.models import Group

# Class
class School(models.Model):
    school = models.CharField(max_length=20)
    logo = models.ImageField(null=True, default='', upload_to='logo/school/')
    email = models.CharField(max_length=20, default=None)
    class Meta:
        db_table = 'School'

class Department(models.Model):
    school = models.ForeignKey(School, on_delete=models.DO_NOTHING)
    department = models.CharField(max_length=50)
    class Meta:
        db_table = 'Department'

# Student
class Profile(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    real_name = models.CharField(max_length=20)
    type = models.SmallIntegerField(default=0)
    profile_image = models.ImageField(null = True, upload_to='profile_image/', default=None)
    school = models.ForeignKey(School, on_delete=models.DO_NOTHING)
    department = models.ForeignKey(Department, on_delete=models.DO_NOTHING, null=True)
    group = models.PositiveSmallIntegerField(default=15)
    rank = models.PositiveBigIntegerField(default=0)
    score = models.IntegerField(default=0)
    last_rank = models.PositiveBigIntegerField(default=0)
    school_last_rank = models.PositiveBigIntegerField(default=0)
    school_rank = models.PositiveBigIntegerField(default=0)
    view_count = models.PositiveBigIntegerField(default=0)
    admission = models.CharField(max_length=10)
    class Meta:
        db_table = "Profile"

class UserSNS(models.Model):
    profile = models.ForeignKey(Profile, on_delete=models.CASCADE, related_name='user_sns')
    url = models.TextField()
    type = models.SmallIntegerField()

# Company
class Company(models.Model):
    logo = models.ImageField(null=True, upload_to = 'logo/company/')
    company_name = models.TextField()

    class Meta:
        db_table = "Company"

class Company_Inform(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, null=True)
    company_name = models.TextField(null = True)
    company_logo = models.ForeignKey(Company, related_name='company_logo', on_delete=models.DO_NOTHING)
    group = models.PositiveSmallIntegerField(default=15)
    location = models.CharField(max_length = 50, null = True)
    information = models.TextField(null=True)
    category = models.CharField(max_length = 20, null=True)
    homepage = models.CharField(max_length = 30, null=True)
    slogan = models.CharField(max_length = 30, null=True)
    view_count = models.IntegerField(default=0)
    type = models.SmallIntegerField(default=0)
    
    class Meta:
        db_table = "Corp_inform"

class ViewCompany(models.Model):
    student = models.ForeignKey(Profile, related_name= 'show_profile', on_delete=models.CASCADE)
    company = models.ForeignKey(Company_Inform, related_name= 'profile_shown', on_delete=models.CASCADE)
    date = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "View_Company"

class CompanyImage(models.Model):
    company_info = models.ForeignKey(Company_Inform, related_name='inform_image', on_delete=models.CASCADE)
    image_info = models.TextField(null=True)
    image = models.ImageField(null=True, upload_to='company/image/%Y%m%d/')

    class Meta:
        db_table = "Company_Image"

class InterestCompany(models.Model):
    company = models.PositiveBigIntegerField()
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)

    class Meta:
        db_table = "Interset_Company"

class Contact(models.Model):
    student = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    company = models.ForeignKey(Company, on_delete=models.CASCADE, related_name = 'scout_company')
    company_name = models.TextField(null = True)        #검색 시 활용
    group = models.ForeignKey(Group, on_delete=models.CASCADE)
    date = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = "Contact"



# Ban
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

# Push alarm list
class Alarm(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='alarm_user')
    alarm_from = models.ForeignKey(User, on_delete=models.CASCADE, related_name='alarm_from')
    type = models.PositiveSmallIntegerField()
    target_id = models.PositiveIntegerField()
    date = models.DateTimeField(auto_now_add=True)
    is_read = models.BooleanField(default=False)
    
    class Meta:
        db_table = "Alarm"

# Ranked User        
class HotUser(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, null=True)
    group = models.PositiveSmallIntegerField(default=15)
    
    class Meta:
        db_table = 'HotUser'
        
#Loop
class Loopship(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='user')
    friend = models.ForeignKey(User, on_delete=models.CASCADE, related_name='loop')

    class Meta:
        db_table = "Loopship"