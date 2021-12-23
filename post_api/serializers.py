from .models import Post, ContentsImage, Like
from project_api.models import Project
from project_api.serializers import SimpleProjectserializer
from rest_framework import serializers

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
        fields = ['id', 'user_id', 'thumbnail', 'title', 'date', 'project', 'like_count']
    
    def get_like_count(self, obj):
        return Like.objects.filter(post_id=obj.id).count()
    
    def get_project(self, obj):
        project = Project.objects.get(id=obj.project_id)
        return SimpleProjectserializer(project).data

class PostingSerializer(serializers.ModelSerializer):
    contents = serializers.SerializerMethodField()
    like = LikeSerializer(many=True, read_only=True)

    class Meta:
        model = Post
        fields = ['id', 'user_id', 'project', 
         'thumbnail', 'title', 'date', 'like', 'contents']
    
    def get_contents(self, obj):
        true = True
        return eval(str(obj.contents))