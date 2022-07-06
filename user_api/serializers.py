from datetime import datetime, timedelta
from project_api.models import Project
from .models import Alarm, Banlist, Profile
from loop.models import Loopship
from post_api.models import Post

from rest_framework import serializers

class ProfileSerializer(serializers.ModelSerializer):
    loop_count = serializers.SerializerMethodField()
    total_post_count = serializers.SerializerMethodField()

    class Meta:
        model = Profile
        fields = ['user_id', 'real_name', 'type', 'profile_image', 'department', 'loop_count', 'total_post_count', 'group']
    
    def get_loop_count(self, obj):
        return Loopship.objects.filter(friend_id=obj.user_id).count()

    def get_total_post_count(self, obj):
        return Post.objects.filter(user_id=obj.user_id).count()

class RankProfileSerailizer(serializers.ModelSerializer):
    recent_post_count = serializers.SerializerMethodField()
    trend = serializers.SerializerMethodField()

    class Meta:
        model = Profile
        fields = ['user_id', 'real_name', 'rank', 'profile_image', 'department', 'recent_post_count', 'trend']
    
    def get_recent_post_count(self, obj):
        now = datetime.now()
        return Post.objects.filter(user_id=obj.user_id).filter(date__range=[now-timedelta(days=30), now]).count()
    
    def get_trend(self, obj):
        return obj.last_lank - obj.rank

class SimpleProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = Profile
        fields = ['user_id', 'real_name', 'profile_image', 'department']

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
                return Post.objects.filter(id=obj.target_id)[0].title
            except IndexError:
                return
    
    def get_profile(self, obj):
        return SimpleProfileSerializer(Profile.objects.filter(user_id=obj.alarm_from_id)[0]).data