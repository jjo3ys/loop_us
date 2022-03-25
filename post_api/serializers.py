from user_api.models import Profile
from user_api.serializers import SimpleProfileSerializer
from tag.models import Post_Tag
from .models import Post, PostImage, Like, Cocomment, Comment
from project_api.models import Project
from rest_framework import serializers

class PostTagSerializer(serializers.ModelSerializer):
    tag = serializers.SerializerMethodField()
    tag_count = serializers.SerializerMethodField()
    class Meta:
        model = Post_Tag
        fields = ['tag_id', 'tag', 'tag_count']
    
    def get_tag(self, obj):
        return obj.tag.tag
    
    def get_tag_count(self, obj):
        return obj.tag.count

class SimpleProjectserializer(serializers.ModelSerializer):
    class Meta:
        model = Project
        fields =['project_id', 'project_name']

class LikeSerializer(serializers.ModelSerializer):
    
    class Meta:
        model = Like
        fields = ['id', 'post_id', 'user_id']
    
class PostingImageSerializer(serializers.ModelSerializer):
    profile = serializers.SerializerMethodField()
    class Meta:
        model = PostImage
        fields = ['id', 'post_id', 'image']

class CocommentSerializer(serializers.ModelSerializer):
    profile = serializers.SerializerMethodField()

    class Meta:
        model = Cocomment
        fields = ['profile', 'cocomment_id', 'content', 'date']
    
    def get_profile(self, obj):
        return SimpleProfileSerializer(Profile.objects.get(user_id=obj.user_id)).data

class CommentSerializer(serializers.ModelSerializer):
    profile = serializers.SerializerMethodField()
    cocomment = serializers.SerializerMethodField()

    class Meta:
        model = Comment
        fields = ['profile', 'comment_id', 'content', 'cocomment', 'date']
    
    def get_profile(self, obj):
        return SimpleProfileSerializer(Profile.objects.get(user_id=obj.user_id)).data
    
    def get_cocomment(self, obj):
        cocomment = Cocomment.objects.filter(comment_id=obj.id)

        return {"cocoments":CocommentSerializer(reversed(list(cocomment)[-3:]), many=True),
                "count":cocomment.count()}

class MainloadSerializer(serializers.ModelSerializer):
    profile = serializers.SerializerMethodField()
    like_count = serializers.SerializerMethodField()
    project = serializers.SerializerMethodField()
    post_tag = PostTagSerializer(many=True, read_only=True)
    image = PostingImageSerializer(many=True, read_only=True)

    class Meta:
        model = Post
        fields = ['id', 'user_id', 'profile', 'title', 'date', 'like_count', 'project', 'image', 'post_tag']

    def get_profile(self, obj):
        return SimpleProfileSerializer(Profile.objects.get(user_id=obj.user_id)).data
    
    def get_like_count(self, obj):
        return Like.objects.filter(post_id=obj.id).count()
    
    def get_project(self, obj):
        return SimpleProjectserializer(obj.project).data
    
class PostingSerializer(serializers.ModelSerializer):
    profile = serializers.SerializerMethodField()
    like_count = serializers.SerializerMethodField()
    project = serializers.SerializerMethodField()
    post_tag = PostTagSerializer(many=True, read_only=True)
    image = PostingImageSerializer(many=True, read_only=True)

    class Meta:
        model = Post
        fields = ['id', 'user_id', 'profile', 'project', 
         'title', 'date', 'like_count', 'contents', 'image', 'post_tag']
        
    def get_profile(self, obj):
        return SimpleProfileSerializer(Profile.objects.get(user_id=obj.user_id)).data
    
    def get_like_count(self, obj):        
        return Like.objects.filter(post_id=obj.id).count()
    
    def get_project(self, obj):
        return SimpleProjectserializer(obj.project).data