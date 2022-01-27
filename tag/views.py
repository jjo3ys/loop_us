from .models import Tag
from .serializer import TagSerializer

from rest_framework import status
from rest_framework.response import Response
from rest_framework.decorators import api_view

# Create your views here.
@api_view(['GET'])
def tag(request):

    return_dict = {}
    return_dict['results'] = []

    tags = Tag.objects.filter(tag__icontains=request.GET['query']).order_by('-count')
    tags = tags[:10]
    return_dict['results'] = TagSerializer(tags, many=True).data

    return Response(return_dict, status=status.HTTP_200_OK)