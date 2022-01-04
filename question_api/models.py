from django.db import models
from django.conf import settings

# Create your models here.


class Question(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    content = models.TextField(null=True)
    adopt = models.BooleanField(null=False)
    date = models.DateField(auto_now_add=True)

    class Meta:
        db_table = "Question"

class Answer(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    question = models.ForeignKey(Question, related_name='answer', on_delete=models.CASCADE)
    content = models.TextField(null=True)
    adopt = models.BooleanField(null=False)
    date = models.DateField(auto_now_add=True)

    class Meta:
        db_table = "Q_answer"

class P2PQuestion(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='user_question', on_delete=models.CASCADE)
    to = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='to_question', on_delete=models.CASCADE)
    content = models.TextField(null=True)
    adopt = models.BooleanField(null=False)
    date = models.DateField(auto_now_add=True)

    class Meta:
        db_table = "Q_p2p_q"    

class P2PAnswer(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    question = models.ForeignKey(P2PQuestion, related_name='p2panswer', on_delete=models.CASCADE)
    content = models.TextField(null=True)
    adopt = models.BooleanField(null=False)
    date = models.DateField(auto_now_add=True)

    class Meta:
        db_table = "Q_p2p_a"