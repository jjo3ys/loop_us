from re import search
from tag.models import Project_Tag
from user_api.models import Profile
from .models import Project
from rest_framework import serializers
from post_api.serializers import PostingSerializer

class ProjectTagSerializer(serializers.ModelSerializer):
    tag = serializers.SerializerMethodField()
    class Meta:
        model = Project_Tag
        fields = ['tag_id', 'tag']
    
    def get_tag(self, obj):
        return obj.tag.tag

class ProjectSerializer(serializers.ModelSerializer):
    posting = PostingSerializer(many=True, read_only=True)
    project_tag = ProjectTagSerializer(many=True, read_only=True)

    class Meta:
        model = Project
        fields = ['id', 'project_name', 'introduction', 'start_date', 'end_date', 'posting', 'project_tag']

class ProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = Profile
        fields = ['user_id', 'real_name', 'profile_image', 'department']