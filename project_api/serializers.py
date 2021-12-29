from tag.models import Project_Tag
from .models import Project, TagLooper
from rest_framework import serializers
from post_api.models import Post, Like
from user_api.models import Profile
from user_api.serializers import SimpleProfileSerializer
from post_api.serializers import PostingSerializer

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
    project_tag = ProjectTagSerializer(many=True, read_only=True)
    looper = ProjectLooperSerializer(many=True, read_only=True)
    like_count = serializers.SerializerMethodField()

    class Meta:
        model = Project
        fields = ['id', 'user_id', 'project_name', 'introduction', 'start_date', 'end_date', 'project_tag', 'looper', 'like_count']
    
    def get_like_count(self, obj):
        post = Post.objects.filter(project_id=obj.id)
        count = 0
        for p in post:
            count+=Like.objects.filter(post_id=p.id).count()
        
        return count

class ProjectPostSerializer(serializers.ModelSerializer):
    project_tag = ProjectTagSerializer(many=True, read_only=True)
    looper = ProjectLooperSerializer(many=True, read_only=True)
    post = PostingSerializer(many=True, read_only=True)
    like_count = serializers.SerializerMethodField()
    
    class Meta:
        model = Project
        fields = ['id', 'project_name', 'introduction', 'start_date', 'end_date', 'project_tag', 'looper', 'like_count', 'post']
    
    def get_like_count(self, obj):
        post = Post.objects.filter(project_id=obj.id)
        count = 0
        for p in post:
            count+=Like.objects.filter(post_id=p.id).count()
        
        return count
