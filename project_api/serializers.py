from .models import Project
from rest_framework import serializers
from post_api.serializers import PostingSerializer


class ProjectSerializer(serializers.ModelSerializer):
    post = PostingSerializer(many=True, read_only=True)

    class Meta:
        model = Project
        fields = ['id', 'project_name', 'introduction', 'start_date', 'end_date', 'post']