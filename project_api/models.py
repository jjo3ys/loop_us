from django.db import models
from django.conf import settings

# Create your models here.
class Project(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    project_name = models.CharField(max_length=50)
    start_date = models.DateField()
    end_date = models.DateField(blank=True, null=True)
    post_count = models.PositiveSmallIntegerField(default=0)

    class Meta:
        db_table = 'Project'

class TagLooper(models.Model):
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name='looper')
    looper = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='looper')

    class Meta:
        db_table = 'Proj_LooperTag'