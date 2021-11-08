from .models import Profile, Tag, Tagging
from django.contrib.auth.models import User
from rest_framework import serializers

class TagSerializer(serializers.ModelSerializer):
    
    class Meta:
        model = Tag
        fields = '__all__'

class TaggingSerailzer(serializers.ModelSerializer):

    class Meta:
        model = Tagging
        fields = ['profile', 'tag']

class ProfileSerializer(serializers.ModelSerializer):

    tagging = TaggingSerailzer(many=True, read_only=True)

    class Meta:
        model = Profile
        fields = ['id', 'user', 'real_name', 'type', 'class_num', 'profile_image', 'tagging']

class UserSerializer(serializers.ModelSerializer):

    profile = ProfileSerializer(many=False, read_only=True)

    class Meta:
        model = User
        fields = ['id', 'username', 'profile']