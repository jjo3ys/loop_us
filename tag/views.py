from .models import Tag
from .serializer import TagSerializer

from rest_framework import status
from rest_framework.response import Response
from rest_framework.decorators import api_view

# Create your views here.
@api_view(['GET'])
def tag(request):
    return_dict = {}
    try:
        tag = Tag.objects.get(tag=request.GET['query'])
        result_list = [tag]
    except:
        result_list = []

    tags = Tag.objects.filter(tag__icontains=request.GET['query']).order_by('-count')
    tags = tags[:10]
    
    for tag in tags:
        if tag not in result_list:
            result_list.append(tag)
            
    return_dict['results'] = TagSerializer(result_list, many=True).data
    return Response(return_dict, status=status.HTTP_200_OK)