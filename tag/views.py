from .models import Tag
from .serializer import TagSerializer

from rest_framework import status
from rest_framework.response import Response
from rest_framework.decorators import api_view

# Create your views here.
@api_view(['POST', 'GET'])
def tag(request):
    if request.method == 'POST':
        tag_sz = TagSerializer(data={'tag':request.data['tag']})
        if tag_sz.is_valid():
            tag_sz.save()
        
        return Response({'tag':tag_sz.data}, status=status.HTTP_201_CREATED)

    elif request.method == 'GET':
        return_dict = {}
        return_dict['results'] = []

        tags = Tag.objects.filter(tag__icontains=request.GET['query']).order_by('-count')
        tags = tags[:10]

        for tag in tags:
            return_dict['results'].append({'id':tag.id,
                                        'tag':tag.tag,
                                        'count':tag.count})

        return Response(return_dict, status=status.HTTP_200_OK)