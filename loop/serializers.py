from .models import Loopship
from user_api.models import Profile

from rest_framework import serializers

class LoopSerializer(serializers.ModelSerializer):
    class Meta:
        model = Loopship
        fields = ['first', 'second']

class ProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = Profile
        fields = ['real_name', 'profile_image']