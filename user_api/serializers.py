from .models import Profile, Tag, Tagging
from django.contrib.auth.models import User
from rest_framework import serializers

class ProfileSerializer(serializers.ModelSerializer):

    class Meta:
        model = Profile
        fields = '__all__'

class UserSerializer(serializers.ModelSerializer):

    profile = ProfileSerializer(many=False, read_only=True)

    class Meta:
        model = User
        fields = ['id', 'username', 'profile']

class TagSerializer(serializers.ModelSerializer):
    
    class Meta:
        model = Tag
        fields = '__all__'

class TaggingSerailzer(serializers.ModelSerializer):

    profile = ProfileSerializer(many=False, read_only=True)
    tag = TagSerializer(many=True, read_only=True)

    class Meta:
        model = Tagging
        fields = ['profile', 'tag']