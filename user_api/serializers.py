from datetime import datetime, timedelta

from project_api.models import Project
from .models import Alarm, Banlist, Profile, School, Department
from loop.models import Loopship
from post_api.models import Post, Cocomment, Comment

from rest_framework import serializers

class SchoolSerializer(serializers.ModelSerializer):
    class Meta:
        model = School
        fields = ['id', 'school', 'email']

class DepSerializer(serializers.ModelSerializer):
    class Meta:
        model = Department
        fields = ['id', 'department']

class ProfileSerializer(serializers.ModelSerializer):
    loop_count = serializers.SerializerMethodField()
    total_post_count = serializers.SerializerMethodField()
    department = serializers.SerializerMethodField()
    school = serializers.SerializerMethodField()

    class Meta:
        model = Profile
        fields = ['user_id', 'real_name', 'type', 'profile_image', 'department', 'loop_count', 'total_post_count', 'group', 'school', 'admission']
    
    def get_loop_count(self, obj):
        return Loopship.objects.filter(friend_id=obj.user_id).count()

    def get_total_post_count(self, obj):
        return Post.objects.filter(user_id=obj.user_id).count()
    
    def get_department(self, obj):
        return obj.department.department

    def get_school(self, obj):
        return obj.school.school

class RankProfileSerailizer(serializers.ModelSerializer):
    recent_post_count = serializers.SerializerMethodField()
    department = serializers.SerializerMethodField()
    school = serializers.SerializerMethodField()

    class Meta:
        model = Profile
        fields = ['user_id', 'real_name', 'rank', 'last_rank', 'profile_image', 'department', 'recent_post_count', 'school']
    
    def get_recent_post_count(self, obj):
        now = datetime.now()
        return Post.objects.filter(user_id=obj.user_id).filter(date__range=[now-timedelta(days=30), now]).count()

    def get_department(self, obj):
        return obj.department.department
    
    def get_school(self, obj):
        return obj.school.school

class SchoolRankProfileSerailizer(serializers.ModelSerializer):
    recent_post_count = serializers.SerializerMethodField()
    department = serializers.SerializerMethodField()
    school = serializers.SerializerMethodField()

    class Meta:
        model = Profile
        fields = ['user_id', 'real_name', 'school_rank', 'school_last_rank', 'profile_image', 'department', 'recent_post_count', 'school']
    
    def get_recent_post_count(self, obj):
        now = datetime.now()
        return Post.objects.filter(user_id=obj.user_id).filter(date__range=[now-timedelta(days=30), now]).count()

    def get_department(self, obj):
        return obj.department.department
    
    def get_school(self, obj):
        return obj.school.school

class SimpleProfileSerializer(serializers.ModelSerializer):
    department = serializers.SerializerMethodField()
    school = serializers.SerializerMethodField()

    class Meta:
        model = Profile
        fields = ['user_id', 'real_name', 'profile_image', 'department', 'school']
    
    def get_department(self, obj):
        return obj.department.department

    def get_school(self, obj):
        return obj.school.school

class BanlistSerializer(serializers.ModelSerializer):
    banlist = serializers.SerializerMethodField()
    class Meta:
        model = Banlist
        fields = ['user_id', 'banlist']
    
    def get_banlist(self, obj):
        ban_list = []
        for ban in obj.banlist:
            ban_list.append(SimpleProfileSerializer(Profile.objects.filter(user_id=ban)[0]).data)
        
        return ban_list

class AlarmSerializer(serializers.ModelSerializer):
    content = serializers.SerializerMethodField()
    profile = serializers.SerializerMethodField()

    class Meta:
        model = Alarm
        fields = ['id', 'user_id', 'type', 'target_id', 'content', 'profile', 'date', 'is_read']
    
    def get_content(self, obj):
        if int(obj.type) == 2:
            return None
        elif int(obj.type) == 3:
            try:
                return Project.objects.filter(id=obj.target_id)[0].project_name
            except IndexError:
                return None
        elif int(obj.type) == 4:
            try:
                return Post.objects.filter(id=obj.target_id)[0].contents
            except IndexError:
                return None
        elif int(obj.type) == 5 or int(obj.type) == 7:
            try:
                return Comment.objects.filter(id=obj.target_id)[0].content
            except IndexError:
                return None
        elif int(obj.type) == 6 or int(obj.type) == 8:
            try:
                return Cocomment.objects.filter(id=obj.target_id)[0].content
            except IndexError:
                return None
    def get_profile(self, obj):
        return SimpleProfileSerializer(Profile.objects.filter(user_id=obj.alarm_from_id)[0]).data