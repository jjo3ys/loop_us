from .models import Post, Contents, ContentsImage, Like
from rest_framework import serializers


class LikeSerializer(serializers.ModelSerializer):
    
    class Meta:
        model = Like
        fields = ['id', 'post_id', 'user_id']
    
class PostingContentsImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = ContentsImage
        fields = ['id', 'post_id', 'image']

class PostingContentsSerializer(serializers.ModelSerializer):
    
    class Meta:
        model = Contents
        fields = ['id', 'post', 'content', 'date']

class PostingSerializer(serializers.ModelSerializer):
    contents = PostingContentsSerializer(many=True, read_only=True)
    contents_image = PostingContentsImageSerializer(many=True, read_only=True)
    like = LikeSerializer(many=True, read_only=True)

    class Meta:
        model = Post
        fields = ['id', 'user_id', 'project', 
         'thumbnail', 'title', 'date', 'like', 'contents', 'contents_image']