from django.db import models
from django.conf import settings
from django.utils import timezone

# Create your models here.
class Project(models.Model):
    project_name = models.CharField(max_length=50, unique=True)
    count = models.IntegerField(default=0)

class Crew(models.Model):
    crew = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    project = models.ForeignKey('Project', related_name='crew', on_delete=models.CASCADE)
    start_date = models.DateField(default=timezone.now())
    end_date = models.DateField(null=True)