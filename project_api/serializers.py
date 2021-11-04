from .models import Project, Crew
from rest_framework import serializers

class CrewSerializer(serializers.ModelSerializer):
    class Meta:
        model = Crew
        fields = '__all__'

class ProjectSerializer(serializers.ModelSerializer):

    crew = CrewSerializer(many=True, read_only=True)

    class Meta:
        model = Project
        fields = ['id', 'project_name', 'crew']