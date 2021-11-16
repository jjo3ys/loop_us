from .models import Profile
from django.contrib.auth.models import User
from rest_framework import serializers


class ProfileSerializer(serializers.ModelSerializer):

    class Meta:
        model = Profile
        fields = ['user', 'real_name', 'type', 'class_num', 'profile_image']

class UserSerializer(serializers.ModelSerializer):

    profile = ProfileSerializer(many=False, read_only=True)

    class Meta:
        model = User
        fields = ['id', 'username', 'profile']