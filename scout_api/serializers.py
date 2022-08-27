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
        field = ['id', 'company_info', 'student_info', 'group_name', 'count', 'date']
    
    def get_company_info(obj):
        return CompanySerializer(obj.contact).data
    
    def get_student_info(obj):
        return SimpleProfileSerializer(obj.student).data

    def get_group_name(obj):
        return obj.group.group_name
    
    def count(obj):
        return Contact.objects.filter(company = obj.company).count()