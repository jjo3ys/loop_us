from rest_framework import serializers

from .models import *

# 뉴스
class NewsSerializer(serializers.ModelSerializer):
    class Meta:
        model = News
        fields = ["urls", "corp"]

# 브런치
class BrunchSerializer(serializers.ModelSerializer):
    class Meta:
        model = Brunch
        fields = ["urls", "writer", "profile_url"]

# 유튜브
class YoutubeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Youtube
        fields = ["urls"]

# 기업 뉴스
class CompanyNewsSerializer(serializers.ModelSerializer):
    class Meta:
        model = CompanyNews
        fields = ['urls', 'corp']