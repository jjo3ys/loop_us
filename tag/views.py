from .models import Tag

from django.contrib.auth.models import User
from rest_framework import status
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated

# Create your views here.
@api_view(['POST', ])
def create_tag(request):
    tag = Tag.objects.create(tag=request.data['tag'])
    
    return Response({'tag':tag}, stauts=status.HTTP_201_CREATED)

@api_view(['GET', ])
def search_tag(request):
    tags = Tag.objects.filter(tag__incontains=request.data['key_word']).order_by('-count')

    return Response({'results':list(tags)[:10]}, status=status.HTTP_200_OK)