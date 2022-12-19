from django.db import models
from tag.models import Group
from user_api.models import Company_Inform
class News(models.Model):
    urls = models.TextField()
    group = models.ForeignKey(Group, related_name='group_news', on_delete=models.DO_NOTHING)
    corp = models.TextField(default=None, null=True)

    class Meta:
        db_table = "News"

class Brunch(models.Model):
    urls = models.TextField()
    group = models.ForeignKey(Group, related_name='group_brunch', on_delete=models.DO_NOTHING)
    writer = models.CharField(max_length=20)
    profile_url = models.TextField(null=True)

    class Meta:
        db_table = "Brunch"

class Youtube(models.Model):
    urls = models.TextField()
    group = models.ForeignKey(Group, related_name='group_youtube', on_delete=models.DO_NOTHING)

    class Meta:
        db_table = "Youtube"
        
class CompanyNews(models.Model):
    urls = models.TextField()
    company = models.ForeignKey(Company_Inform, related_name='company_news', on_delete=models.CASCADE)
    corp = models.TextField(default=None, null=True)
    
    class Meta:
        db_table = "Comapny_News"

class Competition(models.Model):
    group = models.CharField(max_length=20)
    content = models.TextField()
    image = models.TextField()
    organizer = models.CharField(max_length=30)
    start_date = models.DateField()
    end_date = models.DateField()

    class Meta:
        db_table = "Competition"
# Create your models here.
