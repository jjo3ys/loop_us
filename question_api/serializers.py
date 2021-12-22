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

    class Meta:
        model = Answer
        fields = ['id', 'user_id', 'content', 'question_id', 'adopt', 'date']

class QuestionSerializer(serializers.ModelSerializer):
    question_tag = QuestionTagSerialier(many=True, read_only=True)
    answer = AnswerSerializer(many=True, read_only=True)

    class Meta:
        model = Question
        fields = ['id', 'user_id', 'content', 'answer', 'adopt', 'date', 'question_tag']

class OnlyQSerializer(serializers.ModelSerializer):
    question_tag = QuestionTagSerialier(many=True, read_only=True)
    count = serializers.SerializerMethodField()

    class Meta:
        model = Question
        fields = ['id', 'user_id', 'content', 'adopt', 'date', 'question_tag', 'count']
    
    def get_count(self, obj):
        return Answer.objects.filter(question_id=obj.id).count()