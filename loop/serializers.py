from .models import Loopship
from user_api.models import Profile

from rest_framework import serializers

class LoopSerializer(serializers.ModelSerializer):
    class Meta:
        model = Loopship
        fields = ['friend']

class ProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = Profile
        fields = ['user_id', 'real_name', 'profile_image']