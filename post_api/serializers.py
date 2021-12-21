from .models import Post, Contents, ContentsImage, Like
from rest_framework import serializers


class LikeSerializer(serializers.ModelSerializer):
    
    class Meta:
        model = Like
        fields = ['id', 'post_id', 'user_id']
    
class PostingContentsImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = ContentsImage
        fields = ['id', 'contents_id', 'image']

class PostingContentsSerializer(serializers.ModelSerializer):
    contents_image = PostingContentsImageSerializer(many=True, read_only=True)

    class Meta:
        model = Contents
        fields = ['id', 'post', 'content', 'date', 'contents_image']

class PostingSerializer(serializers.ModelSerializer):
    contents = PostingContentsSerializer(many=True, read_only=True)
    like = LikeSerializer(many=True, read_only=True)

    class Meta:
        model = Post
        fields = ['id', 'user_id', 'project', 
         'thumbnail', 'title', 'date', 'like', 'contents']