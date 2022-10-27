from user_api.models import Company, Company_Inform, CompanyImage
from user_api.serializers import CompanySerializer, SimpleProfileSerializer
from .models import Contact
from rest_framework import serializers

class CompanySerializer(serializers.ModelSerializer):
    class Meta:
        model = Company
        fields = ['company_name', 'logo']

class CompanyImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = CompanyImage
        fields = ['image', 'image_info']
        
class CompanyProfileSerializer(serializers.ModelSerializer):
    company_logo = serializers.SerializerMethodField()
    company_images = serializers.SerializerMethodField()

    class Meta:
        model = Company_Inform
        fields = ['user', 'company_logo', 'company_images', 'group', 'category', 'slogan']

    def get_company_logo(self, obj):
        return CompanySerializer(Company.objects.filter(id = obj.company_logo.id)[0]).data
    
    def get_company_images(self, obj):
        return CompanyImageSerializer(CompanyImage.objects.filter(company_info_id = obj.id).first()).data
