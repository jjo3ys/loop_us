from .models import Posting, PostingContents
from rest_framework import serializers

class PostingContentsSerializer(serializers.ModelSerializer):
    class Meta:
        model = PostingContents
        fields = ['posting', 'sequance',
         'contentType', 'content', 'date']

class PostingSerializer(serializers.ModelSerializer):
    
    class Meta:
        model = Posting
        fields = ['author', 'project', 'sequance',
         'thumbnail', 'title', 'date']