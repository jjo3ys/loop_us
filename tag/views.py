from django.core.paginator import Paginator

from post_api.serializers import MainloadSerializer

from .models import Tag, Post_Tag
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
@permission_classes((IsAuthenticated, ))
def tagged_post(request):
    tag_obj = Tag.objects.filter(id=request.GET['id'])[0]
    post_tag_obj = Post_Tag.objects.filter(tag_id=request.GET['id']).select_related('post')
    
    if request.GET['page'] == '1':
        post_list = []
        post_obj = Paginator(post_tag_obj.order_by('-id'), 5).get_page('1')
        for post in post_obj:
            post_list.append(post.post)
        new_post_tag_obj = MainloadSerializer(post_list, many=True).data

        post_list = []
        post_obj = Paginator(post_tag_obj.order_by('-post__like_count'), 5).get_page('1')
        for post in post_obj:
            post_list.append(post.post)
        pop_post_tag_obj = MainloadSerializer(post_list, many=True).data

        return Response({'monthly_count':tag_obj.monthly_count,
                        'related_new':new_post_tag_obj,
                        'related_pop':pop_post_tag_obj}, status=status.HTTP_200_OK)
    else:
        post_list = []

        if request.GET['type'] == 'new':
            post_obj = Paginator(post_tag_obj.order_by('-id'), 5).get_page(request.GET['page'])
            for post in post_obj:
                post_list.append(post.post)

            post_tag_obj = MainloadSerializer(post_list, many=True).data
        
        elif request.GET['type'] == 'pop':
            post_obj = Paginator(post_tag_obj.order_by('-post__like_count'), 5).get_page(request.GET['page'])
            for post in post_obj:
                post_list.append(post.post)

            post_tag_obj = MainloadSerializer(post_list, many=True).data
        
        return Response({'monthly_count':tag_obj.monthly_count,
                         'posting':post_tag_obj}, status=status.HTTP_200_OK)

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