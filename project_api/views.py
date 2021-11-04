from .serializers import ProjectSerializer, CrewSerializer
from .models import Project, Crew

from django.contrib.auth.models import User
from rest_framework import status
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated

# Create your views here.
@api_view(['POST', ])
@permission_classes((IsAuthenticated,))
def create_project(request):
    project_obj = Project(project_name = request.data['project_name'])
    project_sz = ProjectSerializer(project_obj)

    if project_sz.is_valid():
        project_sz.save()
        return Response(project_sz.data, status=status.HTTP_201_CREATED)
    
    else:
        return Response("형식에 맞지 않습니다.", status=status.HTTP_406_NOT_ACCEPTABLE)


@api_view(['POST', ])
@permission_classes((IsAuthenticated,))
def create_crew(request):
    user = request.user

    user_obj = User.objects.get(id=user.id)
    project_obj = Project.objects.get(id=request.data['project_id'])

    crew = Crew(crew = user_obj, 
                project = project_obj,
                start_date = request.data['start_date'],
                end_date = request.data['end_date'])

    crew_sz = CrewSerializer(crew)
    if crew_sz.is_valid():
        crew_sz.save()
        return Response(crew_sz.data, status=status.HTTP_201_CREATED)
    
    else:
        return Response("형식에 맞지 않습니다.", status=status.HTTP_406_NOT_ACCEPTABLE)
    