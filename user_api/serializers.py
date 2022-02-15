from project_api.models import Project
from question_api.models import Question
from .models import Alarm, Banlist, Profile
from .department import DEPARTMENT
from tag.models import Profile_Tag
from loop.models import Loopship
from post_api.models import Post

from rest_framework import serializers

class ProfileTagSerializer(serializers.ModelSerializer):
    tag = serializers.SerializerMethodField()
    tag_count = serializers.SerializerMethodField()
    class Meta:
        model = Profile_Tag
        fields = ['tag_id', 'tag', 'tag_count']
    
    def get_tag(self, obj):
        return obj.tag.tag
    
    def get_tag_count(self, obj):
        return obj.tag.count

class ProfileSerializer(serializers.ModelSerializer):
    profile_tag = ProfileTagSerializer(many=True, read_only=True)
    department = serializers.SerializerMethodField()
    loop_count = serializers.SerializerMethodField()
    total_post_count = serializers.SerializerMethodField()

    class Meta:
        model = Profile
        fields = ['user_id', 'real_name', 'type', 'profile_image', 'department', 'profile_tag', 'loop_count', 'total_post_count']
    
    def get_department(self, obj):
        return DEPARTMENT[obj.department]

    def get_loop_count(self, obj):
        return Loopship.objects.filter(friend_id=obj.user_id).count()

    def get_total_post_count(self, obj):
        return Post.objects.filter(user_id=obj.user_id).count()

class SimpleProfileSerializer(serializers.ModelSerializer):
    department = serializers.SerializerMethodField()
    class Meta:
        model = Profile
        fields = ['user_id', 'real_name', 'profile_image', 'department']

    def get_department(self, obj):
        return DEPARTMENT[obj.department]

class BanlistSerializer(serializers.ModelSerializer):
    banlist = serializers.SerializerMethodField()
    class Meta:
        model = Banlist
        fields = ['user_id', 'banlist']
    
    def get_banlist(self, obj):
        ban_list = []
        for ban in obj.banlist:
            ban_list.append(SimpleProfileSerializer(Profile.objects.get(user_id=ban)).data)
        
        return ban_list

class AlarmSerializer(serializers.ModelSerializer):
    content = serializers.SerializerMethodField()
    profile = serializers.SerializerMethodField()

    class Meta:
        model = Alarm
        fields = ['id', 'user_id', 'type', 'target_id', 'content', 'profile', 'date', 'is_read']
    
    def get_content(self, obj):
        if int(obj.type) == 1:
            try:
                return Question.objects.get(id=obj.target_id).content    
            except Question.DoesNotExist:
                return None    
        elif int(obj.type) == 2:
            return None
        elif int(obj.type) == 3:
            try:
                return Project.objects.get(id=obj.target_id).project_name
            except Project.DoesNotExist:
                return None
        elif int(obj.type) == 4:
            try:
                return Post.objects.get(id=obj.target_id).title
            except Post.DoesNotExist:
                return
    
    def get_profile(self, obj):
        return SimpleProfileSerializer(Profile.objects.get(user_id=obj.alarm_from_id)).data