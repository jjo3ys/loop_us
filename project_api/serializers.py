from django.db.models import Sum

from .models import Project, ProjectUser
from rest_framework import serializers
from post_api.models import Post, Like, PostImage, Comment
from user_api.models import Profile
from user_api.serializers import SimpleProfileSerializer
from post_api.serializers import CommentSerializer, PostTagSerializer, PostingImageSerializer, PostingLinkeSerializer

class PostingSerializer(serializers.ModelSerializer):
    post_tag = PostTagSerializer(many=True, read_only=True)
    contents_image = PostingImageSerializer(many=True, read_only=True)
    comments = serializers.SerializerMethodField()
    contents_link = PostingLinkeSerializer(many=True, read_only=True)

    class Meta:
        model = Post
        fields = ['id', 'user_id', 'date', 'like_count', 'contents', 'contents_image', 'post_tag', 'comments', 'contents_link']
    
    def get_comments(self, obj):
        comments_obj = Comment.objects.filter(post_id=obj.id).order_by('-id')[:10]
        return CommentSerializer(comments_obj, many=True).data
    
class ProjectSerializer(serializers.ModelSerializer):
    thumbnail = serializers.SerializerMethodField()
    post = PostingSerializer(many=True, read_only=True)
    class Meta:
        model = Project
        fields = ['id', 'project_name', 'group', 'thumbnail', 'post', 'post_update_date', 'is_public']

    def get_thumbnail(self, obj):
        if obj.thumbnail == 0: return None
        img_obj = PostImage.objects.filter(id=obj.thumbnail)
        if img_obj:
            return img_obj[0].image.url
        return None
    
class OnlyProjectSerializer(serializers.ModelSerializer):
    thumbnail = serializers.SerializerMethodField()
    class Meta:
        model = Project
        fields = ['id', 'project_name', 'group', 'thumbnail', 'post_update_date', 'is_public']

    def get_thumbnail(self, obj):
        if obj.thumbnail == 0: return None
        img_obj = PostImage.objects.filter(id=obj.thumbnail)
        if img_obj:
            return img_obj[0].image.url
        return None
    
class ProjectUserSerializer(serializers.ModelSerializer):
    manager = serializers.SerializerMethodField()
    member = serializers.SerializerMethodField()
    ratio = serializers.SerializerMethodField()
    project = serializers.SerializerMethodField()
    class Meta:
        model = ProjectUser
        fields = ['user_id', 'project', 'ratio', 'order', 'member', 'manager']
        
    def get_manager(self, obj):
        if obj.is_manager:
            return obj.user_id
        return ProjectUser.objects.filter(project_id=obj.project_id, is_manager=True)[0].user_id
    
    def get_member(self, obj):
        if obj.project.is_public: 
            user_list = list(ProjectUser.objects.filter(project_id=obj.project_id).values_list('user_id', flat=True))
            return SimpleProfileSerializer(Profile.objects.filter(user_id__in=user_list).select_related('school', 'department'), many=True).data
        else:
            return None
    
    def get_ratio(self, obj):
        post_count = Post.objects.filter(user_id=obj.user_id).count()
        if post_count:
            return round(obj.post_count/post_count, 2)
        else: return 0
    
    def get_project(self, obj):
        return ProjectSerializer(obj.project, read_only=True).data

class OnlyProjectUserSerializer(serializers.ModelSerializer):
    manager = serializers.SerializerMethodField()
    member = serializers.SerializerMethodField()
    ratio = serializers.SerializerMethodField()
    project = serializers.SerializerMethodField()
    class Meta:
        model = ProjectUser
        fields = ['user_id', 'project', 'ratio', 'order', 'member', 'manager']
        
    def get_manager(self, obj):
        if obj.is_manager:
            return obj.user_id
        return ProjectUser.objects.filter(project_id=obj.project_id, is_manager=True)[0].user_id
    
    def get_member(self, obj):
        if obj.project.is_public: 
            user_list = list(ProjectUser.objects.filter(project_id=obj.project_id).values_list('user_id', flat=True))
            return SimpleProfileSerializer(Profile.objects.filter(user_id__in=user_list).select_related('school', 'department'), many=True).data
        else:
            return None
    
    def get_ratio(self, obj):
        post_count = Post.objects.filter(user_id=obj.user_id).count()
        if post_count:
            return round(obj.post_count/post_count, 2)
        else: return 0

    def get_project(self, obj):
        return OnlyProjectSerializer(obj.project).data
    
class MemberSerializer(serializers.ModelSerializer):
    profile = serializers.SerializerMethodField()
    class Meta:
        model = ProjectUser
        fields = ['profile', 'is_manager']
        
    def get_profile(self, obj):
        try:
            return SimpleProfileSerializer(Profile.objects.filter(user_id=obj.user_id).select_related('school', 'department')[0]).data
        except:
            return None