from user_api.models import Profile
from user_api.serializers import CompanySerializer, SimpleProfileSerializer
from .models import Contact
from rest_framework import serializers

class ContactSerializers(serializers.ModelSerializer):
    company_info = serializers.SerializerMethodField()
    student_info = serializers.SerializerMethodField()
    group_name = serializers.SerializerMethodField()
    count = serializers.SerializerMethodField()

    class Meta:
        model = Contact
        fields = ['id', 'company_info', 'student_info', 'group_name', 'count', 'date']
    
    def get_company_info(self, obj):
        return CompanySerializer(obj.company).data
    
    def get_student_info(self, obj):
        return SimpleProfileSerializer(Profile.objects.filter(user_id = obj.student)[0]).data

    def get_group_name(self, obj):
        return obj.group.group_name
    
    def get_count(self, obj):
        return Contact.objects.filter(company = obj.company).count()