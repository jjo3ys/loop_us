from crawling_api.models import OutProject, OutsideInform, SchoolNews, ClassProject, SchoolProject
from post_api.serializers import MainloadSerializer
from user_api.serializers import SimpleProfileSerializer
from .serializers import ClassProjectSerializer, OutsideInformSerilizer, ProjectUserSerializer, SchoolNewsSerializer
from .models import Project, ProjectUser
from user_api.models import Company, Profile, Alarm
from user_api.views import ES
# from fcm.models import FcmToken
from fcm.push_fcm import tag_fcm
from post_api.models import Like, BookMark, Post

from rest_framework import status
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated

import datetime
# Create your views here.
@api_view(['POST', 'PUT', 'GET', 'DELETE'])
@permission_classes((IsAuthenticated,))
def project(request):
    user_id = request.user.id
    if request.method == 'POST':
        
        project_obj = Project.objects.create(project_name=request.data['project_name'], is_public=request.data['is_public'])        
        if 'company_id' in request.GET:
            project_obj.tag_company = True
            project_obj.thumbnail = request.GET['company_id']
            project_obj.save()
            user = ES.search(index='profile', body={'query':{'match':{'user_id':{'query':user_id}}}})['hits']['hits'][0]
            text = user['_source']['text']
            text += " "+Company.objects.get(id=request.GET['company_id']).company_name
            id = user['_id']
            ES.update(index='profile', id=id, doc={"text":text})
            
        project_obj = ProjectUser.objects.create(user_id=user_id, project_id=project_obj.id)
        
        return Response(ProjectUserSerializer(project_obj).data, status=status.HTTP_201_CREATED)

    elif request.method == 'PUT':
        type = request.GET['type']
        project_obj = Project.objects.get(id=request.GET['id'])
        if type == 'project_name':
            project_obj.project_name = request.data['project_name']
            if 'company_id' in request.GET:
                project_obj.tag_company = True
                company_id = request.GET['company_id']
                if int(company_id):
                    project_obj.thumbnail = company_id
                    project_obj.save()
                    user = ES.search(index='profile', body={'query':{'match':{'user_id':{'query':user_id}}}})['hits']['hits'][0]
                    text = user['_source']['text']
                    text = text.replace(" "+request.data['company_name'], "")
                    text += " "+Company.objects.get(id=request.GET['company_id']).company_name
                    id = user['_id']
                    ES.update(index='profile', id=id, doc={"text":text})
            project_obj.save()
            
        elif type == 'looper':
            profile_obj = Profile.objects.filter(user_id=user_id)[0]
            looper_list = request.data.getlist('looper')

            for looper in looper_list:
                ProjectUser.objects.create(project_id=project_obj.id, user_id=looper, is_manager=False)
                tag_fcm(looper, profile_obj.real_name, user_id, project_obj.project_name, project_obj.id)
        
        project_obj = ProjectUser.objects.filter(project_id=request.GET['id'], user_id=user_id).select_related('project')[0]            
        return Response(ProjectUserSerializer(project_obj).data, status=status.HTTP_200_OK)

    elif request.method == 'GET':
        try:
            project_obj = ProjectUser.objects.filter(project_id=request.GET['project_id'], user_id=request.GET['user_id']).select_related('project')[0]
        except IndexError:
            return Response(status=status.HTTP_404_NOT_FOUND)
        
        project = ProjectUserSerializer(project_obj).data            
        post_list = list(map(lambda x:x['id'], project['project']['post']))
        like_list = dict(Like.objects.filter(user_id=request.user.id, post_id__in=post_list).values_list('post_id', 'user_id'))
        book_list = dict(BookMark.objects.filter(user_id=request.user.id, post_id__in=post_list).values_list('post_id', 'user_id'))
        for post in project['project']['post']:
            if post['user_id'] == user_id:
                post.update({'is_user':1})
            else:
                post.update({'is_user':0})
            if post['id'] in like_list:
                post.update({"is_liked":1})
            else:
                post.update({"is_liked":0})        
            if post['id'] in book_list:
                post.update({"is_marked":1})
            else:
                post.update({"is_marked":0})

        return Response(project, status=status.HTTP_200_OK)

    elif request.method == 'DELETE':
        project_id = request.GET['id']
        type = request.GET['type']
        if type == 'exit':
            project_obj = ProjectUser.objects.filter(project_id=project_id, user_id=user_id).select_related('project')[0]
            if project_obj.project.tag_company:
                company_obj = Company.objects.filter(id=project_obj.project.thumbnail)
                if company_obj:
                    user = ES.search(index='profile', body={'query':{'match':{'user_id':{'query':user_id}}}})['hits']['hits'][0]
                    text = user['_source']['text']
                    text = text.replace(" "+company_obj[0].company_name, "")
                    id = user['_id']
                    ES.update(index='profile', id=id, doc={"text":text})
            project_obj.delete()
            
        elif type == 'del':
            project_obj = Project.objects.filter(id=project_id)[0]
            if project_obj.tag_company:
                company_obj = Company.objects.filter(id=project_obj.thumbnail)
                if company_obj:
                    user = ES.search(index='profile', body={'query':{'match':{'user_id':{'query':user_id}}}})['hits']['hits'][0]
                    text = user['_source']['text']
                    text = text.replace(" "+company_obj[0].company_name, "")
                    id = user['_id']
                    ES.update(index='profile', id=id, doc={"text":text})
                    
            file_size = 0
            for post in Post.objects.filter(project_id=project_id).prefetch_related('contents_image', 'contents_file'):
                for image in post.contents_image.all():
                    image.image.delete(save=False)
                for file in post.contents_file.all():
                    file_size+=file.file.size
                    file.file.delete(save=False)
                    
            profile_obj = Profile.objects.get(user_id=user_id)     
            profile_obj.upload_size = max(profile_obj.upload_size-file_size, 0)   
            
            Alarm.objects.filter(type__in = [2, 3], target_id=project_id).delete()    
            post_obj = Post.objects.filter(project_id=project_id).values_list('id', flat=True)
            Alarm.objects.filter(target_id__in=post_obj).exclude(type__in=[2, 3]).delete()
            project_obj.delete()
    return Response(status=status.HTTP_200_OK)

@api_view(['GET',])
@permission_classes((IsAuthenticated,))
def in_school(request):
    if request.method == 'GET':
        profile_obj = Profile.objects.select_related('school').get(user_id=request.user.id)
        school = {'school':profile_obj.school.school, 'logo':profile_obj.school.logo.url}
        
        class_obj = ClassProject.objects.select_related('project','class_inform').filter(class_inform__school_id=profile_obj.school_id).order_by('-project__post_update_date')[:3]
        class_obj = ClassProjectSerializer(class_obj, many=True).data
        
        school_act_obj = SchoolNews.objects.filter(school_id=profile_obj.school_id).order_by('-upload_date')[:4]
        school_act_obj = SchoolNewsSerializer(school_act_obj, many=True).data
        result = {
            'school':school,
            'class':class_obj,
            'activity':school_act_obj
        }
        return Response(result, status=status.HTTP_200_OK)

@api_view(['GET',])
@permission_classes((IsAuthenticated,))
def out_school(request):
    if request.method == 'GET':
        if request.GET['type'] == 'pop':
            project_obj = OutsideInform.objects.filter(type=request.GET['cat']).order_by('-view_count')[:10]
        elif request.GET['type'] == 'main':
            project_obj = OutsideInform.objects.filter(type=request.GET['cat'], group=request.GET['group']).order_by('-end_date')[:4]
        return Response(OutsideInformSerilizer(project_obj, many=True).data, status=status.HTTP_200_OK)
            
    
@api_view(['GET',])
@permission_classes((IsAuthenticated,))
def detail(request):
    if request.method == 'GET':
        if request.GET['type'] == 'class':
            project_id = ClassProject.objects.select_related('class_inform').filter(project_id=request.GET['id'])[0].project_id
            
        elif request.GET['type'] == 'school':
            project_obj = SchoolProject.objects.select_related('project', 'school_news').filter(school_news_id=request.GET['id'])
            if project_obj.exists():
                project_id = project_obj[0].project_id
            else: project_id = None
        
        elif request.GET['type'] == 'activity':
            project_obj = OutProject.objects.select_related('project', 'outside_inform').filter(id=request.GET['id'])
            if project_obj.exists():
                project_id = project_obj[0].project_id
            else: project_id = None
            
        project_obj = ProjectUser.objects.filter(project_id=project_id)
        user_list = list(project_obj.values_list('user_id', flat=True))
        member = SimpleProfileSerializer(Profile.objects.filter(user_id__in=user_list).select_related('school', 'department'), many=True).data
        return Response({'member':member, 'project_id':project_id}, status=status.HTTP_200_OK)
    
@api_view(['GET',])
@permission_classes((IsAuthenticated,))
def detail_post(request):
    user_id = request.user.id
    if request.method == 'GET':    
        post_obj = Post.objects.filter(project_id=request.GET['id'], id__lte=request.GET['last'])[:20]
        post_list = list(post_obj.values_list('id', flat=True))
        like_list = dict(Like.objects.filter(user_id=user_id, post_id__in=post_list).values_list('post_id', 'user_id'))
        book_list = dict(BookMark.objects.filter(user_id=user_id, post_id__in=post_list).values_list('post_id', 'user_id'))
        post_obj = MainloadSerializer(post_obj, many=True).data

        for p in post_obj:
            if p['user_id'] == user_id:
                p.update({"is_user":1})
            else:
                p.update({"is_user":0})
            
            if p['id'] in like_list:
                p.update({'is_liked':1})
            else:
                p.update({'is_liked':0})

            if p['id'] in book_list:
                p.update({'is_marked':1})
            else:
                p.update({'is_marked':0})
        return Response(post_obj, status=status.HTTP_200_OK)

# @api_view(['GET',])
# @permission_classes((IsAuthenticated,))
# def out_school(request):
#     if request.method == 'GET':
#         if request.GET['type'] == 'competition':
#             competition_obj = Competition.objects.filter(end_date__gte=datetime.date.today()).order_by('end_date')[:4]