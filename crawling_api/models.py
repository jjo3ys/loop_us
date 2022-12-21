from django.db import models
from tag.models import Group
from user_api.models import Company_Inform, Department, School
from project_api.models import Project
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
    title = models.CharField(max_length=50)
    organizer = models.CharField(max_length=30)
    start_date = models.DateField()
    end_date = models.DateField()
    view_count = models.PositiveIntegerField(default=0)
    tagged_count = models.PositiveIntegerField(default=0)

    class Meta:
        db_table = "Competition"
        
class OutActivity(models.Model):
    group = models.CharField(max_length=20)
    content = models.TextField()
    image = models.TextField()
    title = models.CharField(max_length=50)
    organizer = models.CharField(max_length=30)
    start_date = models.DateField()
    end_date = models.DateField()
    view_count = models.PositiveIntegerField(default=0)
    tagged_count = models.PositiveIntegerField(default=0)

    class Meta:
        db_table = "OutActivity"
        
class SchoolNews(models.Model):
    school = models.ForeignKey(School, related_name='school_news', on_delete=models.DO_NOTHING)
    cat = models.CharField(max_length=20)
    title = models.CharField(max_length=50)
    image = models.TextField()
    url = models.TextField()
    content = models.TextField()
    upload_date = models.DateField()
    view_count = models.PositiveIntegerField(default=0)
    
    class Meta:
        db_table = "School_News"

class ClassInform(models.Model):   
    school = models.ForeignKey(School, related_name='class_school', on_delete=models.CASCADE)
    class_type = models.CharField(max_length=150)
    class_name = models.CharField(max_length=150)
    
    class Meta:
        db_table = "ClassInform"
              
class ClassProject(models.Model):
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name='class_project')
    class_inform = models.ForeignKey(ClassInform, on_delete=models.DO_NOTHING, related_name='class_inform')
    
    class Meta:
        db_table = 'ClassProject'
# Create your models here.
