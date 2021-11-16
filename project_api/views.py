from .serializers import ProjectSerializer
from .models import Project

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

    project_sz = ProjectSerializer(project_obj)

    return Response(project_sz.data, status=status.HTTP_201_CREATED)

@api_view(['GET', ])
@permission_classes((IsAuthenticated,))
def load_project(request, idx):
    return_dict = {}
    user = request.user
    
    project_obj = Project.objects.filter(user=idx)

    project_sz = ProjectSerializer(project_obj, many=True)  
    return_dict.update({'project':project_sz.data})

    if str(user.id) == idx:
        return_dict.update({'is_user':1})
    
    return Response(return_dict, status=status.HTTP_200_OK)