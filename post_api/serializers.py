from user_api.models import Company_Inform, Profile
from user_api.serializers import simpleprofile 
from tag.models import Post_Tag
from .models import Post, PostImage, Like, Cocomment, Comment, PostLink
from project_api.models import Project
from crawling_api.models import News, Brunch, Youtube

from rest_framework import serializers
       
class NewsSerializer(serializers.ModelSerializer):
    class Meta:
        model = News
        fields = ['urls', 'corp']

class BrSerializer(serializers.ModelSerializer):
    class Meta:
        model = Brunch
        fields = ['urls', 'writer', 'profile_url']

class YtSerializer(serializers.ModelSerializer):
    class Meta:
        model = Youtube
        fields = ['urls']

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
        fields = ['image']

class PostingLinkeSerializer(serializers.ModelSerializer):
    class Meta:
        model = PostLink
        fields = ['link']

class CocommentSerializer(serializers.ModelSerializer):
    profile = serializers.SerializerMethodField()
    tagged_user = serializers.SerializerMethodField()

    class Meta:
        model = Cocomment
        fields = ['profile', 'id', 'content', 'date', 'like_count', 'tagged_user']
    
    def get_profile(self, obj):
        profile = simpleprofile(obj)
        return profile
    
    def get_tagged_user(self, obj):
        if obj.tagged == None:
            return None
        else:
            try:
                real_name = Profile.objects.filter(user_id=obj.tagged_id)[0].real_name 
            except:
                real_name = Company_Inform.objects.filter(user_id=obj.tagged_id)[0].company_name
            return {'real_name':real_name, 'user_id':obj.tagged_id}

class CommentSerializer(serializers.ModelSerializer):
    profile = serializers.SerializerMethodField()
    # cocomment_count = serializers.SerializerMethodField()
    cocomments = serializers.SerializerMethodField()
    # cocomments = CocommentSerializer(many=True, read_only=True)

    class Meta:
        model = Comment
        fields = ['profile', 'id', 'content', 'date', 'cocomments', 'like_count']
    
    def get_profile(self, obj):
        profile = simpleprofile(obj)
        return profile

    def get_cocomments(self, obj):
        try:
            cocomment_obj = Cocomment.objects.filter(comment_id=obj.id)
            return {'cocomment':CocommentSerializer(cocomment_obj[:3], many=True).data, 'count':cocomment_obj.count()}
        except:
            return None

    # def get_cocomment_count(self, obj):
    #     return Cocomment.objects.filter(comment_id=obj.id).count()

class MainCommentSerializer(serializers.ModelSerializer):
    profile = serializers.SerializerMethodField()

    class Meta:
        model = Comment
        fields = ['profile', 'content', 'like_count']
    
    def get_profile(self, obj):
        profile = simpleprofile(obj)
        return profile

class MainloadSerializer(serializers.ModelSerializer):
    profile = serializers.SerializerMethodField()
    project = serializers.SerializerMethodField()
    comments = serializers.SerializerMethodField()
    comment_count = serializers.SerializerMethodField()
    post_tag = PostTagSerializer(many=True, read_only=True)
    contents_image = PostingImageSerializer(many=True, read_only=True)
    contents_link = PostingLinkeSerializer(many=True, read_only=True)

    class Meta:
        model = Post
        fields = ['id', 'user_id', 'contents', 'profile', 'date', 'like_count', 'project', 'contents_image', 'post_tag', 'comments', 'contents_link']

    def get_profile(self, obj):
        profile = simpleprofile(obj)
        return profile
    
    def get_project(self, obj):
        return SimpleProjectserializer(obj.project).data
    
    def get_comments(self, obj):
        comment_obj = Comment.objects.filter(post_id=obj.id)
        if comment_obj.count() == 0:
            return []
        else:
            return MainCommentSerializer(comment_obj.order_by('like_count').last()).data
    
    def get_comment_count(self, obj):
        count = 0
        comment_obj = Comment.objects.filter(post_id=obj.id)
        if comment_obj:
            count += comment_obj.count()
            cocomment_obj = Cocomment.objects.filter(comment__post_id=obj.id)
            if comment_obj:
                count += cocomment_obj.count()
                
        return count

class PostingSerializer(serializers.ModelSerializer):
    profile = serializers.SerializerMethodField()
    project = serializers.SerializerMethodField()
    post_tag = PostTagSerializer(many=True, read_only=True)
    contents_image = PostingImageSerializer(many=True, read_only=True)
    comments = serializers.SerializerMethodField()
    contents_link = PostingLinkeSerializer(many=True, read_only=True)

    class Meta:
        model = Post
        fields = ['id', 'user_id', 'profile', 'project', 'date', 'like_count', 'contents', 'contents_image', 'post_tag', 'comments', 'contents_link']
        
    def get_profile(self, obj):
        profile = simpleprofile(obj)
        return profile
    
    def get_project(self, obj):
        return SimpleProjectserializer(obj.project).data
    
    def get_comments(self, obj):
        comments_obj = Comment.objects.filter(post_id=obj.id).order_by('-id')[:10]
        return CommentSerializer(comments_obj, many=True).data