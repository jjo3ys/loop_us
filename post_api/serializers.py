from .models import Posting, PostingContents, PostingContentsImage
from rest_framework import serializers

class PostingContentsImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = PostingContentsImage
        fields = ['id', 'author', 'PostingContents',
         'image']

class PostingContentsSerializer(serializers.ModelSerializer):
    class Meta:
        model = PostingContents
        fields = ['id', 'posting', 'contentType', 'content', 'date']

class PostingSerializer(serializers.ModelSerializer):
    class Meta:
        model = Posting
        fields = ['id', 'author', 'project',
         'thumbnail', 'title', 'date']