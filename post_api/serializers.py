from .models import Post, ContentsImage, Like
from project_api.models import Project
from tag.models import Project_Tag
from rest_framework import serializers

class ProjectTagSerializer(serializers.ModelSerializer):
    tag = serializers.SerializerMethodField()
    class Meta:
        model = Project_Tag
        fields = ['tag_id', 'tag']
    
    def get_tag(self, obj):
        return obj.tag.tag

class SimpleProjectserializer(serializers.ModelSerializer):
    project_tag = ProjectTagSerializer(many=True, read_only=True)
    project_id = serializers.SerializerMethodField()

    class Meta:
        model = Project
        fields =['project_id', 'project_name', 'project_tag']
    
    def get_project_id(self, obj):
        return obj.id

class LikeSerializer(serializers.ModelSerializer):
    
    class Meta:
        model = Like
        fields = ['id', 'post_id', 'user_id']
    
class PostingContentsImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = ContentsImage
        fields = ['id', 'post_id', 'image']

class MainloadSerializer(serializers.ModelSerializer):
    like_count = serializers.SerializerMethodField()
    project = serializers.SerializerMethodField()
    thumbnail = serializers.SerializerMethodField()

    class Meta:
        model = Post
        fields = ['id', 'user_id', 'thumbnail', 'title', 'date', 'like_count', 'project']
    
    def get_like_count(self, obj):
        return Like.objects.filter(post_id=obj.id).count()
    
    def get_project(self, obj):
        return SimpleProjectserializer(obj.project).data
    
    def get_thumbnail(self, obj):
        if obj.thumbnail == '':
            try:
                return ContentsImage.objects.filter(post_id=obj.id)[0].image.url
            except:
                return None
        return obj.thumbnail.url
    
class PostingSerializer(serializers.ModelSerializer):
    contents = serializers.SerializerMethodField()
    like_count = serializers.SerializerMethodField()
    thumbnail = serializers.SerializerMethodField()
    project = serializers.SerializerMethodField()

    class Meta:
        model = Post
        fields = ['id', 'user_id', 'project', 
         'thumbnail', 'title', 'date', 'like_count', 'contents']
    
    def get_contents(self, obj):
        return eval(str(obj.contents))
    
    def get_like_count(self, obj):        
        return Like.objects.filter(post_id=obj.id).count()
    
    def get_project(self, obj):
        return SimpleProjectserializer(obj.project).data
    
    def get_thumbnail(self, obj):
        if obj.thumbnail == '':
            try:
                return ContentsImage.objects.filter(post_id=obj.id)[0].image.url
            except:
                return None
        return obj.thumbnail.url