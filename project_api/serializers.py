from .models import Project, ProjectUser
from rest_framework import serializers
from crawling_api.models import ClassProject, SchoolNews, ClassInform
from post_api.models import Post, PostImage, Comment
from post_api.serializers import MainloadSerializer
from user_api.models import Company, Company_Inform, Profile
from user_api.serializers import SimpleProfileSerializer, simpleprofile
from post_api.serializers import CommentSerializer, PostTagSerializer, PostingImageSerializer, PostingLinkeSerializer

class ClassInformSerializer(serializers.ModelSerializer):
    class Meta:
        model = ClassInform
        fields = '__all__'
        
class SchoolNewsSerializer(serializers.ModelSerializer):
    class Meta:
        model = SchoolNews
        fields = '__all__'

class PostingSerializer(serializers.ModelSerializer):
    post_tag = PostTagSerializer(many=True, read_only=True)
    contents_image = PostingImageSerializer(many=True, read_only=True)
    comments = serializers.SerializerMethodField()
    contents_link = PostingLinkeSerializer(many=True, read_only=True)

    class Meta:
        model = Post
        fields = ['id', 'user_id', 'date', 'like_count', 'contents', 'contents_image', 'post_tag', 'comments', 'contents_link']
    
    def get_comments(self, obj):
        comments_obj = Comment.objects.filter(post_id=obj.id).order_by('-id')[:10]
        return CommentSerializer(comments_obj, many=True).data
    
class ProjectSerializer(serializers.ModelSerializer):
    thumbnail = serializers.SerializerMethodField()
    post = PostingSerializer(many=True, read_only=True)
    class Meta:
        model = Project
        fields = ['id', 'project_name', 'group', 'thumbnail', 'post', 'post_update_date', 'is_public']

    def get_thumbnail(self, obj):
        if obj.thumbnail == 0: return None
        elif obj.tag_company:
            img_obj = Company.objects.filter(id=obj.thumbnail)
            company_profile = Company_Inform.objects.filter(company_logo_id=obj.thumbnail)
            if img_obj and company_profile:
                return {'company_logo':img_obj[0].logo.url, 'user_id':company_profile[0].user_id, 'company_name':company_profile[0].company_name}
            elif img_obj:
                return {'company_logo':img_obj[0].logo.url, 'user_id':None, 'company_name':img_obj[0].company_name}
        else:
            img_obj = PostImage.objects.filter(id=obj.thumbnail)
            if img_obj:
                return img_obj[0].image.url
        return None
    
class OnlyProjectSerializer(serializers.ModelSerializer):
    thumbnail = serializers.SerializerMethodField()
    class Meta:
        model = Project
        fields = ['id', 'project_name', 'group', 'thumbnail', 'post_update_date', 'is_public']

    def get_thumbnail(self, obj):
        if obj.thumbnail == 0: return None
        elif obj.tag_company:
            img_obj = Company.objects.filter(id=obj.thumbnail)
            if img_obj:
                return img_obj[0].logo.url
        else:
            img_obj = PostImage.objects.filter(id=obj.thumbnail)
            
            if img_obj:
                return img_obj[0].image.url
        return None
    
class ProjectUserSerializer(serializers.ModelSerializer):
    manager = serializers.SerializerMethodField()
    member = serializers.SerializerMethodField()
    ratio = serializers.SerializerMethodField()
    project = serializers.SerializerMethodField()
    class Meta:
        model = ProjectUser
        fields = ['user_id', 'project', 'ratio', 'post_count', 'order', 'member', 'manager']
        
    def get_manager(self, obj):
        if obj.is_manager:
            return obj.user_id
        return ProjectUser.objects.filter(project_id=obj.project_id, is_manager=True)[0].user_id
    
    def get_member(self, obj):
        if obj.project.is_public: 
            user_list = list(ProjectUser.objects.filter(project_id=obj.project_id).values_list('user_id', flat=True))
            return SimpleProfileSerializer(Profile.objects.filter(user_id__in=user_list).select_related('school', 'department'), many=True).data
        else:
            return None
    
    def get_ratio(self, obj):
        post_count = Post.objects.filter(user_id=obj.user_id).count()
        if post_count:
            return round(obj.post_count/post_count, 2)
        else: return 0
    
    def get_project(self, obj):
        return ProjectSerializer(obj.project, read_only=True).data

class OnlyProjectUserSerializer(serializers.ModelSerializer):
    manager = serializers.SerializerMethodField()
    member = serializers.SerializerMethodField()
    ratio = serializers.SerializerMethodField()
    project = serializers.SerializerMethodField()
    class Meta:
        model = ProjectUser
        fields = ['user_id', 'project', 'ratio', 'post_count', 'order', 'member', 'manager']
        
    def get_manager(self, obj):
        if obj.is_manager:
            return obj.user_id
        return ProjectUser.objects.filter(project_id=obj.project_id, is_manager=True)[0].user_id
    
    def get_member(self, obj):
        if obj.project.is_public: 
            user_list = list(ProjectUser.objects.filter(project_id=obj.project_id).values_list('user_id', flat=True))
            return SimpleProfileSerializer(Profile.objects.filter(user_id__in=user_list).select_related('school', 'department'), many=True).data
        else:
            return None
    
    def get_ratio(self, obj):
        post_count = Post.objects.filter(user_id=obj.user_id).count()
        if post_count:
            return round(obj.post_count/post_count, 2)
        else: return 0

    def get_project(self, obj):
        return OnlyProjectSerializer(obj.project).data
    
class MemberSerializer(serializers.ModelSerializer):
    profile = serializers.SerializerMethodField()
    class Meta:
        model = ProjectUser
        fields = ['profile', 'is_manager']
        
    def get_profile(self, obj):
        profile = simpleprofile(obj)
        return profile

class ClassProjectSerializer(serializers.ModelSerializer):
    class_inform = ClassInformSerializer()
    project = OnlyProjectSerializer()
    member = serializers.SerializerMethodField()
    class Meta:
        model = ClassProject
        fields = ['class_inform', 'project', 'member']
        
    def get_member(self, obj):
        project_obj = ProjectUser.objects.filter(project_id=obj.project_id)
        user_list = list(project_obj.order_by('?')[:3].values_list('user_id', flat=True))
        return {'profile':SimpleProfileSerializer(Profile.objects.filter(user_id__in=user_list).select_related('school', 'department'), many=True).data,
                'count':project_obj.count()}
        
class DetailSerializer(serializers.ModelSerializer):
    class_inform = ClassInformSerializer()
    member = serializers.SerializerMethodField()
    class Meta:
        model = ClassProject
        fields = ['class_inform', 'project', 'member']
        
    def get_member(self, obj):
        project_obj = ProjectUser.objects.filter(project_id=obj.project_id)
        user_list = list(project_obj.values_list('user_id', flat=True))
        return SimpleProfileSerializer(Profile.objects.filter(user_id__in=user_list).select_related('school', 'department'), many=True).data