from rest_framework import serializers

from .models import Log

from user_api.models import Profile
from user_api.serializers import SimpleProfileSerializer

class LogSerializer(serializers.ModelSerializer):
    data = serializers.SerializerMethodField()
    class Meta:
        model = Log
        fields = ['type', 'data']
    
    def get_data(self, obj):
        if obj.type == 1:
            return SimpleProfileSerializer(Profile.objects.filter(user_id=int(obj.query))).data
        else:
            return obj.query