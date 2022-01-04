from django.db import models
from project_api.models import Project
from user_api.models import Profile
from question_api.models import Question
# Create your models here.
class Tag(models.Model):
    tag = models.CharField(max_length=50, unique=True)
    count = models.IntegerField(default=1)

    class Meta:
        db_table = "Tag"

class Project_Tag(models.Model):
    tag = models.ForeignKey('Tag', related_name='project_tag', on_delete=models.DO_NOTHING)
    project = models.ForeignKey(Project, related_name='project_tag', on_delete=models.CASCADE)

    class Meta:
        db_table = "Proj_tag"

class Profile_Tag(models.Model):
    tag = models.ForeignKey('Tag', related_name='profile_tag', on_delete=models.DO_NOTHING)
    profile = models.ForeignKey(Profile, related_name='profile_tag', on_delete=models.CASCADE)

    class Meta:
        db_table = 'Prof_tag'

class Question_Tag(models.Model):
    tag = models.ForeignKey('Tag', related_name='question_tag', on_delete=models.DO_NOTHING)
    question = models.ForeignKey(Question, related_name='question_tag', on_delete=models.CASCADE)

    class Meta:
        db_table = 'Q_tag'