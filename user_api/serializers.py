from .models import Profile
from tag.models import Profile_Tag
from project_api.serializers import ProjectSerializer

from django.contrib.auth.models import User
from rest_framework import serializers


class ProfileTagSerializer(serializers.ModelSerializer):
    tag = serializers.SerializerMethodField()
    class Meta:
        model = Profile_Tag
        fields = ['tag_id', 'tag']
    
    def get_tag(self, obj):
        return obj.tag.tag


class ProfileSerializer(serializers.ModelSerializer):
    tag = ProfileTagSerializer(many=True, read_only=True)
    project = ProjectSerializer(many=True, read_only=True)

    class Meta:
        model = Profile
        fields = ['user', 'real_name', 'type', 'class_num', 'profile_image', 'tag', 'project']

class UserSerializer(serializers.ModelSerializer):
    profile = ProfileSerializer(many=False, read_only=True)

    class Meta:
        model = User
        fields = ['id', 'username', 'profile']