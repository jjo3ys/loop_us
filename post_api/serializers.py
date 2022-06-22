from user_api.models import Profile
from user_api.serializers import SimpleProfileSerializer
from tag.models import Post_Tag
from .models import CommentLike, Post, PostImage, Like, Cocomment, Comment
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
        fields =['id', 'project_name']

class LikeSerializer(serializers.ModelSerializer):
    
    class Meta:
        model = Like
        fields = ['id', 'post_id', 'user_id']
    
class PostingImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = PostImage
        fields = ['id', 'post_id', 'image']

class CocommentSerializer(serializers.ModelSerializer):
    profile = serializers.SerializerMethodField()
    tagged_user = serializers.SerializerMethodField()

    class Meta:
        model = Cocomment
        fields = ['profile', 'id', 'content', 'date', 'like_count', 'tagged_user']
    
    def get_profile(self, obj):
        return SimpleProfileSerializer(Profile.objects.get(user_id=obj.user_id)).data
    
    def get_tagged_user(self, obj):
        if obj.tagged == None:
            return None
        else: return {'real_name':Profile.objects.get(user_id=obj.tagged.id).real_name, 'user_id':obj.tagged.id}

class CommentSerializer(serializers.ModelSerializer):
    profile = serializers.SerializerMethodField()
    cocomment_count = serializers.SerializerMethodField()
    cocomments = CocommentSerializer(many=True, read_only=True)

    class Meta:
        model = Comment
        fields = ['profile', 'id', 'content', 'cocomment_count', 'date', 'cocomments', 'like_count']
    
    def get_profile(self, obj):
        return SimpleProfileSerializer(Profile.objects.get(user_id=obj.user_id)).data
    
    def get_cocomment_count(self, obj):
        return Cocomment.objects.filter(comment_id=obj.id).count()

class MainCommentSerializer(serializers.ModelSerializer):
    profile = serializers.SerializerMethodField()

    class Meta:
        model = Comment
        fields = ['profile', 'content', 'like_count']
    
    def get_profile(self, obj):
        profile_obj = Profile.objects.get(user_id=obj.user_id)
        return {'real_name':profile_obj.real_name, 'user_id':obj.user_id}

class MainloadSerializer(serializers.ModelSerializer):
    profile = serializers.SerializerMethodField()
    project = serializers.SerializerMethodField()
    comments = serializers.SerializerMethodField()
    post_tag = PostTagSerializer(many=True, read_only=True)
    contents_image = PostingImageSerializer(many=True, read_only=True)

    class Meta:
        model = Post
        fields = ['id', 'user_id', 'contents', 'profile', 'date', 'like_count', 'project', 'contents_image', 'post_tag', 'comments']

    def get_profile(self, obj):
        return SimpleProfileSerializer(Profile.objects.get(user_id=obj.user_id)).data
    
    def get_project(self, obj):
        return SimpleProjectserializer(obj.project).data
    
    def get_comments(self, obj):
        comment_obj = Comment.objects.filter(post_id=obj.id)
        comment_like_obj = CommentLike.objects.filter(comment_id__in=comment_obj.values_list('id', flat=True))
        if comment_like_obj.count() > 0:
            return MainCommentSerializer(comment_obj.order_by('-like_count')[0]).data
        else:
            if len(comment_obj) == 0:
                return []
            else:
                return MainCommentSerializer(list(comment_obj)[-1]).data

class PostingSerializer(serializers.ModelSerializer):
    profile = serializers.SerializerMethodField()
    project = serializers.SerializerMethodField()
    post_tag = PostTagSerializer(many=True, read_only=True)
    contents_image = PostingImageSerializer(many=True, read_only=True)
    comments = CommentSerializer(many=True, read_only=True)

    class Meta:
        model = Post
        fields = ['id', 'user_id', 'profile', 'project', 'date', 'like_count', 'contents', 'contents_image', 'post_tag', 'comments']
        
    def get_profile(self, obj):
        return SimpleProfileSerializer(Profile.objects.get(user_id=obj.user_id)).data
    
    def get_project(self, obj):
        return SimpleProjectserializer(obj.project).data