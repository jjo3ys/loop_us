from django.db import models
from django.conf import settings

# Create your models here.


class Question(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL,
                             on_delete=models.CASCADE)
    content = models.TextField(null=True)
    adopt = models.BooleanField(null=False)
    date = models.DateField(auto_now_add=True)

    class Meta:
        db_table = "Question_question"


class Answer(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL,
                             on_delete=models.CASCADE)
    question = models.ForeignKey(
        Question, related_name='answers', on_delete=models.CASCADE)
    content = models.TextField(null=True)
    adopt = models.BooleanField(null=False)
    date = models.DateField(auto_now_add=True)

    class Meta:
        db_table = "Question_answer"
