from django.db import models
from career.models import Group, Career
from user.models import Company_Inform, School

# Crawling Data
class News(models.Model):
    urls = models.TextField()
    group = models.ForeignKey(Group, related_name="group_news", on_delete=models.DO_NOTHING, default=15)
    corp = models.TextField(default=None, null=True)

    class Meta:
        db_table = "News"

class Brunch(models.Model):
    urls = models.TextField()
    group = models.ForeignKey(Group, related_name="group_brunch", on_delete=models.DO_NOTHING, default=15)
    writer = models.CharField(max_length=20)
    profile_url = models.TextField(null=True)

    class Meta:
        db_table = "Brunch"

class Youtube(models.Model):
    urls = models.TextField()
    group = models.ForeignKey(Group, related_name="group_youtube", on_delete=models.DO_NOTHING, default=15)

    class Meta:
        db_table = "Youtube"
        
class CompanyNews(models.Model):
    urls = models.TextField()
    company = models.ForeignKey(Company_Inform, related_name="company_news", on_delete=models.CASCADE)
    corp = models.TextField(default=None, null=True)
    
    class Meta:
        db_table = "Comapny_News"