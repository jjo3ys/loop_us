from .models import Question, Answer

from rest_framework import serializers


class AnswerSerializer(serializers.ModelSerializer):
    answerer = serializers.SerializerMethodField('get_username_to_answer')

    class Meta:
        model = Answer
        fields = ['id', 'user', 'answerer',
                  'content', 'question', 'adopt', 'date']

    def get_username_to_answer(self, answer):
        username = answer.user.username
        return username


class QuestionSerializer(serializers.ModelSerializer):
    questioner = serializers.SerializerMethodField('get_username_to_question')
    answers = AnswerSerializer(many=True, read_only=True)

    class Meta:
        model = Question
        fields = ['id', 'user', 'questioner',
                  'content', 'answers', 'adopt', 'date']

    def get_username_to_question(self, question):
        username = question.user.username
        return username
