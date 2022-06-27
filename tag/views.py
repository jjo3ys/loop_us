from .models import Tag
from .serializer import TagSerializer

from search.models import InterestTag
from search.views import interest_tag

from rest_framework import status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import api_view, permission_classes

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

@api_view(['GET'])
@permission_classes((IsAuthenticated,))
def search_tag(request):
    return_dict = {}
    try:
        tag = Tag.objects.filter(tag=request.GET['query'])[0]
        result_list = [tag]
        interest_list = InterestTag.objects.get_or_create(user_id=request.user.id)[0]
        interest_list = interest_tag(interest_list, 'plus', tag.id, 20)
        interest_list.save()
    except:
        result_list = []

    tags = Tag.objects.filter(tag__icontains=request.GET['query']).order_by('-count')[:10]
    
    for tag in tags:
        if tag not in result_list:
            result_list.append(tag)
            
    return_dict['results'] = TagSerializer(result_list, many=True).data
    return Response(return_dict, status=status.HTTP_200_OK)