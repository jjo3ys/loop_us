from .models import Post, ContentsImage, Like
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

    class Meta:
        model = Post
        fields = ['id', 'user_id', 'thumbnail', 'title', 'date', 'like_count']
    
    def get_like_count(self, obj):
        return Like.objects.filter(post_id=obj.id).count()

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