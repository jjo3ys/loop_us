from rest_framework import serializers

from portfolio_api.models import Element, Portfolio
from post_api.models import ContentsImage, Post
from project_api.models import Project

from user_api.models import Profile
from user_api.serializers import SimpleProfileSerializer


class PortfolioSerializers(serializers.ModelSerializer):
    
    class Meta:
        model = Portfolio
        fields = ['id', 'user_id', 'introduction', 'date']

class ElementSerializers(serializers.ModelSerializer):

    class Meta:
        model  = Element
        fields = ['id', 'title', 'date', 'contents', 'portfolio_id', 'image']

class PortfolioElementSerializers(serializers.ModelSerializer):
    profile = serializers.SerializerMethodField()
    element = ElementSerializers(many = True, read_only=True)
    
    class Meta:
        model = Portfolio
        fields = ['id', 'user_id','profile', 'introduction', 'date', 'element']
    
    def get_profile(self, obj):
        return SimpleProfileSerializer(Profile.objects.get(user_id=obj.user_id)).data

class SelectImageSerializers(serializers.ModelSerializer):
    project = serializers.SerializerMethodField()
    post_thumbnail = serializers.SerializerMethodField()

    class Meta:
        model = ContentsImage
        fields= ['id', 'project', 'post_thumbnail', 'post_id', 'image']
    
    def get_project(self, obj):
        project = {}
        project_obj = Project.objects.get(id= Post.objects.get(id=obj.post.id).project.id)
        project['project_id'] = project_obj.id
        project['project_name'] = project_obj.project_name    

        if project_obj.pj_thumbnail == '':
            project['pj_thumbnail'] = None
        else: 
            project['pj_thumbnail'] = project_obj.pj_thumbnail.url
        return project
    
    def get_post_thumbnail(self, obj):
        post_obj = Post.objects.get(id=obj.post.id)
        if post_obj.thumbnail == '':
            return None
        return post_obj.thumbnail.url
    


    

