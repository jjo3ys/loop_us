from .models import Posting, PostingContents, PostingContentsImage
from rest_framework import serializers

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
    username = serializers.SerializerMethodField('get_username_from_author')


    class Meta:
        model = Posting
        fields = ['id', 'author', 'username', 'project', 
         'thumbnail', 'title', 'date', 'posting_content']

    def get_username_from_author(self, posting):
        username = posting.author.username
        return username