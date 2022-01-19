from .models import Question, Answer#, P2PQuestion, P2PAnswer
from tag.models import Question_Tag
from user_api.models import Profile
from user_api.serializers import SimpleProfileSerializer
from rest_framework import serializers

class QuestionTagSerialier(serializers.ModelSerializer):
    tag = serializers.SerializerMethodField()
    tag_count = serializers.SerializerMethodField()
    class Meta:
        model = Question_Tag
        fields = ['tag_id', 'tag', 'tag_count']
    
    def get_tag(self, obj):
        return obj.tag.tag

    def get_tag_count(self, obj):
        return obj.tag.count


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

# class P2PAnswerSerializer(serializers.ModelSerializer):
#     user_profile = serializers.SerializerMethodField()

#     class Meta:
#         model = P2PAnswer
#         fields = ['id', 'user_profile', 'content', 'question_id', 'date']

#     def get_user_profile(self, obj):
#         profile_obj = Profile.objects.get(user_id=obj.user.id)
#         return SimpleProfileSerializer(profile_obj).data

# class P2PQuestionSerializer(serializers.ModelSerializer):
#     p2panswer = P2PAnswerSerializer(many=True, read_only=True)
#     user_profile = serializers.SerializerMethodField()
#     to_profile = serializers.SerializerMethodField()

#     class Meta:
#         model = P2PQuestion
#         fields = ['id', 'user_profile', 'to_profile', 'content', 'date', 'p2panswer']
    
#     def get_user_profile(self, obj):
#         profile_obj = Profile.objects.get(user_id=obj.user.id)
#         return SimpleProfileSerializer(profile_obj).data
    
#     def get_to_profile(self, obj):
#         profile_obj = Profile.objects.get(user_id=obj.to.id)
#         return SimpleProfileSerializer(profile_obj).data