from django.db import models
from django.conf import settings

# Create your models here.
class Project(models.Model):
    project_name = models.CharField(max_length=50)
    post_update_date = models.DateTimeField(null=True, default=None)
    group = models.PositiveSmallIntegerField(default=10)
    thumbnail = models.PositiveBigIntegerField(null=True, default=0)
    is_public = models.BooleanField(default=False)
    class Meta:
        db_table = 'Project'

class ProjectUser(models.Model):
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name='looper')
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='looper')
    post_count = models.PositiveSmallIntegerField(default=0)
    order = models.PositiveSmallIntegerField(default=None, null=True)

    class Meta:
        db_table = 'ProjectUser'