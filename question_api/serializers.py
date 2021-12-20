from .models import Question, Answer
from tag.models import Question_Tag
from user_api.models import Profile
from rest_framework import serializers

class QuestionTagSerialier(serializers.ModelSerializer):
    tag = serializers.SerializerMethodField()
    class Meta:
        model = Question_Tag
        fields = ['tag_id', 'tag']
    
    def get_tag(self, obj):
        return obj.tag.tag


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
    question_tag = QuestionTagSerialier(many=True, read_only=True)
    questioner = serializers.SerializerMethodField('get_username_to_question')
    answers = AnswerSerializer(many=True, read_only=True)

    class Meta:
        model = Question
        fields = ['id', 'user', 'questioner',
                  'content', 'answers', 'adopt', 'date', 'question_tag']

    def get_username_to_question(self, question):
        username = question.user.username
        return username
