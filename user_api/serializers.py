from datetime import datetime, timedelta
from crawling_api.models import CompanyNews

from project_api.models import Project
from scout_api.serializers import CompanyImageSerializer
from .models import Alarm, Banlist, Company, Company_Inform, CompanyImage, Profile, School, Department, UserSNS, ViewCompany
from loop.models import Loopship
from post_api.models import Post, Cocomment, Comment

from rest_framework import serializers

def simpleprofile(obj):
    try:
        return SimpleProfileSerializer(Profile.objects.filter(user_id=obj.user_id).select_related('school', 'department')[0]).data
    except:
        try:
            return SimpleComapnyProfileSerializer(Company_Inform.objects.filter(user_id=obj.user_id).select_related('company_logo')[0]).data
        except: return None

class SchoolSerializer(serializers.ModelSerializer):
    class Meta:
        model = School
        fields = ['id', 'school', 'email']

class DepSerializer(serializers.ModelSerializer):
    class Meta:
        model = Department
        fields = ['id', 'department']
        
class SNSSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserSNS
        fields = ['id', 'type', 'url']

class ProfileSerializer(serializers.ModelSerializer):
    user_sns = SNSSerializer(many=True)
    follower_count = serializers.SerializerMethodField()
    following_count = serializers.SerializerMethodField()
    total_post_count = serializers.SerializerMethodField()
    department = serializers.SerializerMethodField()
    school = serializers.SerializerMethodField()

    class Meta:
        model = Profile
        fields = ['user_id', 'real_name', 'type', 'profile_image', 'department', 'follower_count', 'following_count', 'total_post_count', 'group', 'school', 'admission', 'user_sns']
    
    def get_follower_count(self, obj):
        return Loopship.objects.filter(friend_id=obj.user_id).count()

    def get_following_count(self, obj):
        return Loopship.objects.filter(user_id=obj.user_id).count()

    def get_total_post_count(self, obj):
        return Post.objects.filter(user_id=obj.user_id).count()
    
    def get_department(self, obj):
        return obj.department.department

    def get_school(self, obj):
        return {'school_name':obj.school.school, 'logo':obj.school.logo.url}

class RankProfileSerailizer(serializers.ModelSerializer):
    recent_post_count = serializers.SerializerMethodField()
    department = serializers.SerializerMethodField()
    school_name = serializers.SerializerMethodField()

    class Meta:
        model = Profile
        fields = ['user_id', 'real_name', 'rank', 'last_rank', 'profile_image', 'department', 'recent_post_count', 'school_name']
    
    def get_recent_post_count(self, obj):
        now = datetime.now()
        return Post.objects.filter(user_id=obj.user_id).filter(date__range=[now-timedelta(days=30), now]).count()

    def get_department(self, obj):
        return obj.department.department
    
    def get_school_name(self, obj):
        return obj.school.school

class SchoolRankProfileSerailizer(serializers.ModelSerializer):
    recent_post_count = serializers.SerializerMethodField()
    department = serializers.SerializerMethodField()
    school_name = serializers.SerializerMethodField()

    class Meta:
        model = Profile
        fields = ['user_id', 'real_name', 'school_rank', 'school_last_rank', 'profile_image', 'department', 'recent_post_count', 'school_name']
    
    def get_recent_post_count(self, obj):
        now = datetime.now()
        return Post.objects.filter(user_id=obj.user_id).filter(date__range=[now-timedelta(days=30), now]).count()

    def get_department(self, obj):
        return obj.department.department
    
    def get_school_name(self, obj):
        return obj.school.school

class SimpleProfileSerializer(serializers.ModelSerializer):
    department = serializers.SerializerMethodField()
    school_name = serializers.SerializerMethodField()

    class Meta:
        model = Profile
        fields = ['user_id', 'real_name', 'profile_image', 'department', 'school_name']
    
    def get_department(self, obj):
        return obj.department.department

    def get_school_name(self, obj):
        return obj.school.school

class BanlistSerializer(serializers.ModelSerializer):
    banlist = serializers.SerializerMethodField()
    class Meta:
        model = Banlist
        fields = ['user_id', 'banlist']
    
    def get_banlist(self, obj):
        ban_list = []

        banned_stu = SimpleProfileSerializer(Profile.objects.filter(user_id__in = obj.banlist).select_related('school', 'department'), many=True).data
        banned_com = SimpleComapnyProfileSerializer(Company_Inform.objects.filter(user_id__in = obj.banlist).select_related('company_logo'), many=True).data
        return banned_stu + banned_com

class AlarmSerializer(serializers.ModelSerializer):
    content = serializers.SerializerMethodField()
    profile = serializers.SerializerMethodField()

    class Meta:
        model = Alarm
        fields = ['id', 'user_id', 'type', 'target_id', 'content', 'profile', 'date', 'is_read']
    
    def get_content(self, obj):
        type = int(obj.type)
        
        if type == 3:
            try:
                return Project.objects.filter(id=obj.target_id)[0].project_name
            except IndexError:
                return None
        elif type in [9, 11]:
            return Post.objects.filter(id=obj.target_id).select_related('project')[0].project.project_name
        else:
            return None
                
    def get_profile(self, obj):
        obj.user_id = obj.alarm_from_id
        profile = simpleprofile(obj)
        return profile

class SearchCompanySerializer(serializers.ModelSerializer):

    class Meta:
        model = Company
        fields = "__all__"

class CompanySerializer(serializers.ModelSerializer):

    class Meta:
        model = Company
        fields = ['logo', 'company_name']
        
class CompanyNewsSerializer(serializers.ModelSerializer):
    class Meta:
        model = CompanyNews
        fields = ['urls', 'corp']
        
class SimpleComapnyProfileSerializer(serializers.ModelSerializer):
    company_logo = CompanySerializer()
    class Meta:
        model = Company_Inform
        fields = ['company_logo', 'user_id', 'group', 'category', 'location']

class CompanyProfileSerializer(serializers.ModelSerializer):
    company_logo = serializers.SerializerMethodField()
    company_images = serializers.SerializerMethodField()
    news = serializers.SerializerMethodField()

    class Meta:
        model = Company_Inform
        fields = ['company_logo','company_name', 'information', 'location', 'category', 'homepage', 'user_id', 'slogan', 'group', 'company_images', 'type', 'news']
    
    def get_company_logo(self, obj):
        return Company.objects.filter(id = obj.company_logo.id)[0].logo.url
    
    def get_company_images(self, obj):
        return CompanyImageSerializer(CompanyImage.objects.filter(company_info = obj), many = True).data
    
    def get_news(self, obj):
        return CompanyNewsSerializer(CompanyNews.objects.filter(company_id=obj.id), many=True).data

class ViewProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = ViewCompany
        fields = ['user', 'shown']