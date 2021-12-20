from .models import Loopship
from user_api.models import Profile

from rest_framework import serializers

class LoopSerializer(serializers.ModelSerializer):
    class Meta:
        model = Loopship
        fields = ['friend']