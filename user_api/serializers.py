from .models import Profile
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