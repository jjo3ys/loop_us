from .models import Post, ContentsImage, Like
from rest_framework import serializers
import json

class LikeSerializer(serializers.ModelSerializer):
    
    class Meta:
        model = Like
        fields = ['id', 'post_id', 'user_id']
    
class PostingContentsImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = ContentsImage
        fields = ['id', 'post_id', 'image']

class PostingSerializer(serializers.ModelSerializer):
    contents = serializers.SerializerMethodField()
    like = LikeSerializer(many=True, read_only=True)

    class Meta:
        model = Post
        fields = ['id', 'user_id', 'project', 
         'thumbnail', 'title', 'date', 'like', 'contents']
    
    def get_contents(self, obj):
        true = True
        return eval(obj.contents)