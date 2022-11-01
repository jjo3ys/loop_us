from tag.models import Group
from user_api.models import Company, Company_Inform, CompanyImage, InterestCompany
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
    interest_count = serializers.SerializerMethodField()

    class Meta:
        model = Company_Inform
        fields = ['user_id', 'company_name', 'company_logo', 'location', 'company_images', 'group', 'category', 'slogan', 'interest_count']

    def get_company_logo(self, obj):
        return Company.objects.filter(id = obj.company_logo.id)[0].logo.url
    
    def get_company_images(self, obj):
        return CompanyImage.objects.filter(company_info_id = obj.id).first().image.url
    
    def get_interest_count(self, obj):
        return InterestCompany.objects.filter(company = obj.id).count()

class GroupSerializers(serializers.ModelSerializer):
    companies = serializers.SerializerMethodField()
    
    class Meta:
        model = Group
        fields = ['id', 'companies']
    
    def get_companies(self, obj):
        return CompanyProfileSerializer(Company_Inform.objects.filter(group = obj.id).order_by('?')[:5], many = True).data