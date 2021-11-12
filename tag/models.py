from django.db import models
from project_api.models import Project
from user_api.models import Profile

# Create your models here.
class Tag(models.Model):
    tag = models.CharField(max_length=50)
    count = models.IntegerField(default=1)

    class Meta:
        db_table = "tag"

class Project_Tag(models.Model):
    tag = models.ForeignKey('Tag', related_name='project_tag', on_delete=models.DO_NOTHING)
    project = models.ForeignKey(Project, related_name='project_tag', on_delete=models.CASCADE)

    class Meta:
        db_table = "project_tag"

class Profile_Tag(models.Model):
    tag = models.ForeignKey('Tag', related_name='profile_tag', on_delete=models.DO_NOTHING)
    profile = models.ForeignKey(Profile, related_name='profile_tag', on_delete=models.CASCADE)

    class Meta:
        db_table = 'profile_tag'