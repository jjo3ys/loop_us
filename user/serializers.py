from rest_framework import serializers

from .models import *
from .utils import loop, loop_count

from career.models import *
from career.serializers import *

from data.models import *
from data.serializers import *

# 간단 프로필 리스트
class ProfileListSerializer(serializers.ModelSerializer):
    department   = serializers.SerializerMethodField()
    school       = serializers.SerializerMethodField()
    relationship = serializers.SerializerMethodField()

    class Meta:
        model = Profile
        fields = ["user_id", "real_name", "profile_image"
                  "department", "school"]
    
    def get_department(self, obj):
        return obj.department.department

    def get_school(self, obj):
        return obj.school.school

# 사용자와의 관계가 있는 프로필 리스트
class ProfileListWithLoopSerializer(ProfileListSerializer):
    relationship = serializers.SerializerMethodField()

    class Meta:
        model = Profile
        fields = ["user_id", "real_name", "profile_image"
                  "department", "school", "relationship"]
    
    def get_relationship(self, obj):
        user_id = self.context.get("user_id")
        looped = loop(user_id, obj.user_id)

        if obj.user_id == user_id: 
            return {"is_user":1}
        return {"is_user":0, "looped":looped}

# 기본 회사 정보
class SearchCompanySerializer(serializers.ModelSerializer):
    class Meta:
        model = Company
        fields = "__all__"

# 회사 로고
class LogoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Company
        fields = ["logo", "company_name"]

# 간단 회사 프로필 리스트
class CompanyProfileListSerializer(serializers.ModelSerializer):
    company_logo = LogoSerializer()
    class Meta:
        model = Company_Inform
        fields = ["user_id", "group", "category", "location",
                  "company_logo"]
# 회사 소개용 이미지
class InformImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = CompanyImage
        fields = ["image", "image_info"]

# 회사 프로필
class CompanyProfileSerializer(serializers.ModelSerializer):
    viewd_profile = serializers.SerializerMethodField()
    relationship  = serializers.SerializerMethodField()
    company_logo  = serializers.SerializerMethodField()
    loop_count    = serializers.SerializerMethodField()
    company_news  = CompanyNewsSerializer(many=True, read_only=True)
    inform_image  = InformImageSerializer(many=True, read_only=True)

    class Meta:
        model = Company_Inform
        fields = ["company_name", "information", "location", "category", "homepage", "user_id", "slogan", "group", "type",
                  "viewd_profile", "relationship", "loop_count", "company_logo", 
                  "company_news",  "inform_image"]
    
    # 기업 프로필을 봤던 학생들 리스트  
    def get_viewd_profile(self, obj):          
        viewd_list = ViewCompany.objects.filter(comapny_id = obj.user_id).order_by("-date").select_related("show_profile__department", "show_profile__school")[:100]
        viewd_list = list(map(lambda x: x.student, viewd_list))
        return ProfileListSerializer(self.context.get("vied_list"), many=True).data
    
    # 사용자와의 관계
    def get_relationship(self, obj):
        user_id = self.context.get("user_id")
        if user_id == obj.user_id:
            follow_obj = Loopship.objects.filter(user_id=user_id)
            following_obj = Loopship.objects.filter(friend_id=user_id)
            return {"is_user":1,
                    "follow_count":follow_obj.count(),
                    "following_count":following_obj.count()}
        else:
            looped = loop(user_id, obj.user_id)                  
            return {"is_user":0, "looped":looped}
    
    # 프로필 주인 팔로우 팔로잉 카운트
    def get_loop_count(self, obj):
        return loop_count(obj.user_id)

    def get_company_logo(self, obj):
        return obj.company_logo.logo.url

# 학교 리스트
class SchoolSerializer(serializers.ModelSerializer):
    class Meta:
        model = School
        fields = ["id", "school", "email"]

# 학과 리스트
class DepSerializer(serializers.ModelSerializer):
    class Meta:
        model = Department
        fields = ["id", "department"]

# 학생 사용자 sns
class SNSSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserSNS
        fields = ["id", "type", "url"]   

# 학생 프로필
class ProfileSerializer(serializers.ModelSerializer):
    department   = serializers.SerializerMethodField()
    school       = serializers.SerializerMethodField()
    post_count   = serializers.SerializerMethodField()
    relationship = serializers.SerializerMethodField()
    loop_count    = serializers.SerializerMethodField()
    user_sns     = SNSSerializer(many=True, read_only=True)

    class Meta:
        model = Profile
        fields = ["user_id", "real_name", "type", "profile_image", "admission",
                  "department", "school", "post_count", "relationship", 
                  "user_sns"]
    
    def get_department(self, obj):
        return obj.department.department
    
    def get_school(self, obj):
        return obj.school.school
    
    def get_post_count(self, obj):
        return Post.objects.filter(user_id=obj.user_id).count()
    
    # 사용자와의 관계
    def get_relationship(self, obj):
        user_id = self.context.get("user_id")
        if user_id == obj.user_id:
            alarm = False
            if Alarm.objects.filter(user_id = user_id, is_read = False).exists(): 
                alarm = True
            return {"is_user":1, "alarm":alarm}
        else:
            looped = loop(user_id, obj.user_id)
            return {"is_user":0, "looped":looped}
    
    # 프로필 주인 팔로우 팔로잉 카운트
    def get_loop_count(self, obj):
        return loop_count(obj.user_id)

# 알람 리스트
class AlarmSerializer(serializers.ModelSerializer):
    content = serializers.SerializerMethodField()
    profile = serializers.SerializerMethodField()

    class Meta:
        model = Alarm
        fields = ["id", "user_id", "type", "target_id", "date", "is_read",
                  "content", "profile"]

    # 알람 타입에 따른 내용 전달
    def get_content(self, obj):
        alarm_type = obj.type
        content = None
        if alarm_type == 3:
            try:
                content = Career.objects.get(id=obj.target_id).career_name
            except Career.DoesNotExist: pass
        elif alarm_type in [9, 11]:
            try:
                content = Post.objects.select_related("career").get(id=obj.target_id).career.career_name
            except Post.DoesNotExist: pass

        return content
    
    def get_profile(self, obj):
        return ProfileListSerializer(obj.alarm_from.profile, read_only=True).data
        
# 유저 밴리스트
class BanlistSerializer(serializers.ModelSerializer):
    banlist = serializers.SerializerMethodField()

    class Meta:
        model = Banlist
        fields = ["user_id", 
                  "banlist"]
    
    def get_banlist(self, obj):
        return ProfileListSerializer(Profile.objects.filter(user_id__in=obj.banlist), many=True, read_only=True).data