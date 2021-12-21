from re import search
from tag.models import Project_Tag
from .models import Project, TagLooper
from rest_framework import serializers
from post_api.serializers import PostingSerializer
from user_api.models import Profile
from user_api.serializers import SimpleProfileSerializer

class ProjectTagSerializer(serializers.ModelSerializer):
    tag = serializers.SerializerMethodField()
    class Meta:
        model = Project_Tag
        fields = ['tag_id', 'tag']
    
    def get_tag(self, obj):
        return obj.tag.tag

class ProjectLooperSerializer(serializers.ModelSerializer):
    profile = serializers.SerializerMethodField()
    class Meta:
        model = TagLooper
        fields = ['profile']
    
    def get_profile(self, obj):
        profile = Profile.objects.get(user_id=obj.looper.id)
        return SimpleProfileSerializer(profile).data

class ProjectSerializer(serializers.ModelSerializer):
    post = PostingSerializer(many=True, read_only=True)
    project_tag = ProjectTagSerializer(many=True, read_only=True)
    looper = ProjectLooperSerializer(many=True, read_only=True)

    class Meta:
        model = Project
        fields = ['id', 'project_name', 'introduction', 'start_date', 'end_date', 'post', 'project_tag', 'looper']