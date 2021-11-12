from .models import Tag
from .serializer import TagSerializer

from django.contrib.auth.models import User

from rest_framework import status
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated

# Create your views here.
@api_view(['POST', ])
def create_tag(request):
    tag_sz = TagSerializer(data={'tag':request.data['tag']})
    if tag_sz.is_valid():
        tag_sz.save()
    
    return Response({'tag':tag_sz.data}, status=status.HTTP_201_CREATED)

@api_view(['GET', ])
def search_tag(request):
    return_dict = {}
    return_dict['results'] = []

    tags = Tag.objects.filter(tag__icontains=request.GET['query']).order_by('-count')
    tags = tags[:10]

    for tag in tags:
        return_dict['results'].append({'id':tag.id,
                                       'tag':tag.tag})

    return Response(return_dict, status=status.HTTP_200_OK)