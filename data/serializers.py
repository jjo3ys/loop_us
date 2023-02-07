from rest_framework import serializers

from .models import *

class CompanyNewsSerializer(serializers.ModelSerializer):
    class Meta:
        model = CompanyNews
        fields = ['urls', 'corp']