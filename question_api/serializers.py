from .models import Question, Answer

from rest_framework import serializers


class QuestionSerializer(serializers.ModelSerializer):
    username = serializers.SerializerMethodField('get_username_from_author')

    class Meta:
        model = Question
        fields = ['id', 'user', 'username', 'content',
                  'adopt', 'date']

    def get_username_from_author(self, question):
        username = question.user.username
        return username


class AnswerSerializer(serializers.ModelSerializer):
    username = serializers.SerializerMethodField('get_username_from_author')

    class Meta:
        model = Answer
        fields = ['id', 'user', 'username', 'content',
                  'adopt', 'date']

    def get_username_from_author(self, answer):
        username = answer.user.username
        return username
