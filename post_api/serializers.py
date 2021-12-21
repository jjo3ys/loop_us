from .models import Posting, PostingContents, PostingContentsImage, Like
from rest_framework import serializers


class LikeSerializer(serializers.ModelSerializer):
    
    class Meta:
        model = Like
        fields = ['id', 'posting', 'user']
    
class PostingContentsImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = PostingContentsImage
        fields = ['id', 'author', 'PostingContents',
         'image']

class PostingContentsSerializer(serializers.ModelSerializer):
    posting_image = PostingContentsImageSerializer(many=True, read_only=True)

    class Meta:
        model = PostingContents
        fields = ['id', 'posting', 'contentType', 'content','date', 'posting_image']

class PostingSerializer(serializers.ModelSerializer):
    posting_content = PostingContentsSerializer(many=True, read_only=True)
    like = LikeSerializer(many=True, read_only=True)

    class Meta:
        model = Posting
        fields = ['id', 'user_id', 'project', 
         'thumbnail', 'title', 'date', 'like', 'posting_content']