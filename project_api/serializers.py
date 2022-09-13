from .models import Project, ProjectUser
from rest_framework import serializers
from post_api.models import Post, Like, PostImage
from user_api.models import Profile
from user_api.serializers import SimpleProfileSerializer
from post_api.serializers import PostingSerializer


class ProjectSerializer(serializers.ModelSerializer):
    thumbnail = serializers.SerializerMethodField()
    class Meta:
        model = Project
        fields = ['id', 'project_name', 'group', 'thumbnail', 'post_update_date', 'is_public']

    def get_thumbnail(self, obj):
        if obj.thumbnail == 0: return None
        img_obj = PostImage.objects.filter(id=obj.thumbnail)[0]
        if img_obj:
            return img_obj.image.url
        return None

class ProjectUserSerializer(serializers.ModelSerializer):
    profile = serializers.SerializerMethodField()
    project = serializers.SerializerMethodField()
    class Meta:
        model = ProjectUser
        fields = ['user_id', 'project', 'post_count', 'order', 'profile']
    
    def get_profile(self, obj):
        try:
            return SimpleProfileSerializer(Profile.objects.filter(user_id=obj.user_id)[0]).data
        except:
            return None
    
    def get_project(self, obj):
        return ProjectSerializer(obj.project, read_only=True).data

class ProjectPostSerializer(serializers.ModelSerializer):
    looper = ProjectUserSerializer(many=True, read_only=True)
    post = PostingSerializer(many=True, read_only=True)
    count = serializers.SerializerMethodField()
    profile = serializers.SerializerMethodField()
    
    class Meta:
        model = Project
        fields = ['id', 'profile', 'project_name', 'looper', 'count', 'post']
    
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
