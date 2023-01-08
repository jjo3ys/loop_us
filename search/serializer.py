from rest_framework import serializers

from .models import Log

from tag.models import Tag
from tag.serializer import TagSerializer
from user_api.models import Profile, Company_Inform
from user_api.serializers import SimpleProfileSerializer, SimpleComapnyProfileSerializer

class LogSerializer(serializers.ModelSerializer):
    data = serializers.SerializerMethodField()
    class Meta:
        model = Log
        fields = ['id', 'type', 'data']
    
    def get_data(self, obj):
        try:
            if obj.type == 0:
                return SimpleProfileSerializer(Profile.objects.filter(user_id=int(obj.query))[0]).data
            elif obj.type == 2:
                return TagSerializer(Tag.objects.filter(id=int(obj.query))[0]).data
            elif obj.type == 3:
                return SimpleComapnyProfileSerializer(Company_Inform.objects.filter(user_id=int(obj.query)).select_related('company_logo')[0]).data
            else:
                return obj.query
        except IndexError:
            return None