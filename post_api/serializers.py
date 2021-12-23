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
    
    class Meta:
        model = Project
        fields =['id', 'project_name', 'project_tag']

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

    class Meta:
        model = Post
        fields = ['id', 'user_id', 'thumbnail', 'title', 'date', 'like_count', 'project']
    
    def get_like_count(self, obj):
        return Like.objects.filter(post_id=obj.id).count()
    
    def get_project(self, obj):
        return SimpleProjectserializer(obj.project).data
    
class PostingSerializer(serializers.ModelSerializer):
    contents = serializers.SerializerMethodField()
    like_count = serializers.SerializerMethodField()

    class Meta:
        model = Post
        fields = ['id', 'user_id', 'project', 
         'thumbnail', 'title', 'date', 'like_count', 'contents']
    
    def get_contents(self, obj):
        true = True
        return eval(str(obj.contents))
    
    def get_like_count(self, obj):
        count = 0
        post = Post.objects.filter(id=obj.id)
        for p in post:
            count += Like.objects.filter(post_id=p.id).count()
        
        return count