import re
from .serializers import ProjectSerializer, ProjectTagSerializer, ProjectPostSerializer
from .models import Project, TagLooper
from tag.models import Tag, Project_Tag
from user_api.models import Profile
from user_api.serializers import SimpleProfileSerializer
from fcm.models import FcmToken
from fcm.push_fcm import tag_fcm

from django.contrib.auth.models import User
from rest_framework import status
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated

# Create your views here.
@api_view(['POST', ])
@permission_classes((IsAuthenticated,))
def create_project(request):
    user = request.user

    start_date = request.data['start_date']
    end_date = request.data['end_date']

    if request.data['end_date'] == '':
        end_date = None

    profile_obj = Profile.objects.get(user_id=user.id)    
    project_obj = Project.objects.create(user=user, project_name = request.data['project_name'], 
                                         introduction = request.data['introduction'],
                                         start_date = start_date,
                                         end_date = end_date,
                                         pj_thumbnail = request.FILES.get('thumbnail'))
    
    for looper in eval(request.data['looper']):
        TagLooper.objects.create(project=project_obj, looper_id=looper)
        try:
            token = FcmToken.objects.get(user_id=looper)
            tag_fcm(token.token, profile_obj.real_name)
        except:
            pass

    for tag in eval(request.data['tag']):
        try:
            tag_obj = Tag.objects.get(tag=tag)
            tag_obj.count = tag_obj.count + 1
            tag_obj.save()

        except Tag.DoesNotExist:
            tag_obj = Tag.objects.create(tag = tag)
        
        Project_Tag.objects.create(project=project_obj, tag=tag_obj)

    project_sz = ProjectSerializer(project_obj)
    return Response(project_sz.data, status=status.HTTP_201_CREATED)

@api_view(['POST', ])
@permission_classes((IsAuthenticated,))
def update_project(request, idx):
    start_date = request.data['start_date']
    end_date = request.data['end_date']
    tag_list = eval(request.data['tag'])
    looper_list = eval(request.data['looper'])

    if request.data['end_date'] == '':
        end_date = None
    
    profile_obj = Profile.objects.get(user_id=request.user.id)
    project_obj = Project.objects.get(id=idx)
    project_obj.project_name = request.data['project_name']
    project_obj.introduction = request.data['introduction']
    project_obj.start_date = start_date
    project_obj.end_date = end_date
    if type(request.data['thumbnail'])==str:
        pass
    else:
        project_obj.pj_thumbnail = request.FILES.get('thumbnail')
        
    project_obj.save()
    old_looper = TagLooper.objects.filter(project_id=project_obj.id)

    for looper in old_looper:
        if looper.looper.id not in looper_list:
            looper.delete()

    for looper in looper_list:
        looper, valid = TagLooper.objects.get_or_create(project_id=project_obj.id, looper_id=looper)
        if valid:
            try:
                token = FcmToken.objects.get(user_id=looper)
                tag_fcm(token.token, profile_obj.real_name)
            except:
                pass

    old_tag = Project_Tag.objects.filter(project=idx)
    old_sz = ProjectTagSerializer(old_tag, many=True)
    old_tag = old_sz.data
    old_list = []

    for tag in old_tag:
        old_list.append(tag['tag'])

        if tag['tag'] not in tag_list:
            project_tag = Project_Tag.objects.get(tag_id = tag['tag_id'], project = project_obj)
            project_tag.tag.count = project_tag.tag.count - 1
            if project_tag.tag.count == 0:
                project_tag.tag.delete()
            else:    
                project_tag.tag.save()

    for tag in tag_list:
        if tag not in old_list: 
            try:
                tag_obj = Tag.objects.get(tag=tag)
                tag_obj.count = tag_obj.count + 1
                tag_obj.save()

            except Tag.DoesNotExist:
                tag_obj = Tag.objects.create(tag = tag)

            Project_Tag.objects.create(tag = tag_obj, project = project_obj)

    project_sz = ProjectSerializer(project_obj)
    return Response(project_sz.data, status=status.HTTP_200_OK)

@api_view(['POST', ])
@permission_classes((IsAuthenticated,))
def delete_project(request, idx):
    project_obj = Project.objects.get(id=idx)
    project_obj.delete()
    return Response("is deleted", status=status.HTTP_200_OK)

@api_view(['GET', ])
@permission_classes((IsAuthenticated,))
def load_project(request, idx):
    project_obj = Project.objects.get(id=idx)
    project = ProjectPostSerializer(project_obj).data
    profile_obj = Profile.objects.get(user=project_obj.user)
    profile_obj = SimpleProfileSerializer(profile_obj).data
    project.update(profile_obj)
    if request.user.id == project_obj.user_id:
        project.update({"is_user":1})
    else:
        project.update({"is_user":0})

    return Response(project, status=status.HTTP_200_OK)