from django.db import models
from django.conf import settings

# Create your models here.
class Project(models.Model):
    id = models.AutoField(db_column='id', primary_key=True)
    project_name = models.CharField(max_length=50, unique=True)
    count = models.IntegerField(default=1)

class Crew(models.Model):
    crew = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    project = models.ForeignKey('Project', related_name='crew', on_delete=models.CASCADE)
    start_date = models.DateField()
    end_date = models.DateField(null=True)