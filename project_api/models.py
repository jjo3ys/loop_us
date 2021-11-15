from django.db import models
from django.conf import settings

# Create your models here.
class Project(models.Model):
    id = models.AutoField(db_column='id', primary_key=True)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    project_name = models.CharField(max_length=50)
    introduction = models.CharField(max_length=100)
    start_date = models.DateField()
    end_date = models.DateField(blank=True, null=True)

    class Meta:
        db_table = 'project'