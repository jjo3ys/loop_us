from rest_framework import serializers

from .models import Log

from user_api.models import Profile, Company_Inform
from user_api.serializers import SimpleProfileSerializer, SimpleComapnyProfileSerializer

class LogSerializer(serializers.ModelSerializer):
    data = serializers.SerializerMethodField()
    class Meta:
        model = Log
        fields = ['id', 'type', 'data']
    
    def get_data(self, obj):
        if obj.type == 0:
            return SimpleProfileSerializer(Profile.objects.filter(user_id=int(obj.query))).data
        elif obj.type == 3:
            return SimpleComapnyProfileSerializer(Company_Inform.objects.filter(user_id=int(obj.query))).data
        else:
            return obj.query