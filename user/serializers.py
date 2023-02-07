from rest_framework import serializers

from .models import *

from career.models import *
from career.serializers import *

from data.models import *
from data.serializers import *

class InformImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = CompanyImage
        fields = ['image', 'image_info']

class ViewCompanyProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = ViewCompany
        fields = ['user', 'shown']

class CompanyProfileSerializer(serializers.ModelSerializer):
    viewd_profile = serializers.SerializerMethodField()
    company_logo  = serializers.SerializerMethodField
    company_news  = CompanyNewsSerializer(many=True, read_only=True)
    inform_image  = InformImageSerializer(many=True, read_only=True)

    class Meta:
        model = Company_Inform
        fields = ['company_name', 'information', 'location', 'category', 'homepage', 'user_id', 'slogan', 'group', 'type',
                  'company_logo', 'company_news',  'inform_image']
    
    def get_viewd_profile(self, obj):
        return ViewCompanyProfileSerializer()
    
    def get_company_logo(self, obj):
        return obj.company_logo.logo.url
    
