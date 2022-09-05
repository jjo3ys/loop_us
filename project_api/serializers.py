from .models import Project, TagLooper
from rest_framework import serializers
from post_api.models import Post, Like
from user_api.models import Profile
from user_api.serializers import SimpleProfileSerializer
from post_api.serializers import PostingSerializer

class ProjectLooperSerializer(serializers.ModelSerializer):
    profile = serializers.SerializerMethodField()
    class Meta:
        model = TagLooper
        fields = ['profile']
    
    def get_profile(self, obj):
        try:
            return SimpleProfileSerializer(Profile.objects.filter(user_id=obj.looper_id)[0]).data
        except:
            return None

class ProjectSerializer(serializers.ModelSerializer):
    looper = ProjectLooperSerializer(many=True, read_only=True)
    class Meta:
        model = Project
        fields = ['id', 'user_id', 'project_name', 'start_date', 'end_date', 'post_count', 'looper', 'group', 'post_update_date']

class ProjectPostSerializer(serializers.ModelSerializer):
    looper = ProjectLooperSerializer(many=True, read_only=True)
    post = PostingSerializer(many=True, read_only=True)
    count = serializers.SerializerMethodField()
    profile = serializers.SerializerMethodField()
    
    class Meta:
        model = Project
        fields = ['id', 'profile', 'project_name', 'start_date', 'end_date', 'looper', 'count', 'post']
    
    def get_count(self, obj):
        post = Post.objects.filter(project_id=obj.id)
        post_id = post.values_list('id', flat=True)
        
        count=Like.objects.filter(post_id__in = post_id).count()
        
        return {"post_count":post.count(), "like_count":count}
    
    def get_profile(self, obj):
        try:
            return SimpleProfileSerializer(Profile.objects.filter(user_id=obj.user_id)[0]).data
        except:
            return None
