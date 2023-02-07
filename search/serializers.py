from rest_framework import serializers

from .models import Log

from career.models import Tag
from career.serializers import TagSerializer

from user.models import Profile, Company_Inform
from user.serializers import ProfileListSerializer, CompanyProfileListSerializer

# 검색 기록 리스트
class LogSerializer(serializers.ModelSerializer):
    log = serializers.SerializerMethodField()

    class Meta:
        model = Log
        fields = ["id", "type",
                  "data"]
    
    # 타입에 따른 검색 기록
    def get_data(self, obj):
        log_type = obj.type
        query    = obj.query
        try:
            if log_type == 0:
                data = ProfileListSerializer(Profile.objects.get(user_id=query), read_only=True).data
            elif log_type == 2:
                data = TagSerializer(Tag.objects.get(id=query), read_only=True).data
            elif log_type == 3:
                data = CompanyProfileListSerializer(Company_Inform.objects.get(user_id=query), read_only=True).data
            else: data = query
        except:
            data = None
        return data