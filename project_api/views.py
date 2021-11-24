from .serializers import ProjectSerializer, ProjectTagSerializer
from .models import Project
from tag.models import Tag, Project_Tag

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
        
    project_obj = Project.objects.create(user=user, project_name = request.data['project_name'], 
                                         introduction = request.data['introduction'],
                                         start_date = start_date,
                                         end_date = end_date)

    for tag in request.data['tag']:
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
    tag_list = request.data['tag']

    if request.data['end_date'] == '':
        end_date = None
        
    project_obj = Project.objects.get(id=idx)
    project_obj.project_name = request.data['project_name']
    project_obj.introduction = request.data['introduction']
    project_obj.start_date = start_date
    project_obj.end_date = end_date
    project_obj.save()

    old_tag = Project_Tag.objects.filter(project=idx)
    old_sz = ProjectTagSerializer(old_tag, many=True)
    old_tag = old_sz.data
    old_list = []

    for tag in old_tag:
        old_list.append(tag['tag'])

        if tag['tag'] not in tag_list:
            Project_Tag.objects.get(tag_id = tag['tag_id'], project = project_obj).delete()
            tag_obj = Tag.objects.get(id=tag['tag_id'])
            tag_obj.count = tag_obj.count - 1
            if tag_obj.count == 0:
                tag_obj.delete()
            else:    
                tag_obj.save()

    for tag in tag_list:
        if tag in old_list:
            continue
        else: 
            try:
                tag_obj = Tag.objects.get(tag=tag)
                tag_obj.count = tag_obj.count + 1
                tag_obj.save()

            except Tag.DoesNotExist:
                tag_obj = Tag.objects.create(tag = tag)

            Project_Tag.objects.create(tag = tag_obj, project = project_obj)

    project_sz = ProjectSerializer(project_obj)
    return Response(project_sz.data, status=status.HTTP_200_OK)

@api_view(['GET', ])
@permission_classes((IsAuthenticated,))
def load_project(request, idx):
    return_dict = {}
    user = request.user
 
    project_obj = Project.objects.get(id=idx)
    project_sz = ProjectSerializer(project_obj)  
    print(project_sz)
    return_dict.update({'project':project_sz.data})

    if str(user.id) == project_obj.id:
        return_dict.update({'is_user':1})
    
    return Response(return_dict, status=status.HTTP_200_OK)
