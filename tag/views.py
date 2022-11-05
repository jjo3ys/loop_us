from datetime import date

from django.core.paginator import Paginator
from post_api.models import BookMark, Like

from post_api.serializers import MainloadSerializer

from .models import Tag, Post_Tag
from .serializer import TagSerializer

# from search.models import InterestTag
# from search.views import interest_tag

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
    user_id = request.user.id
    post_tag_obj = Post_Tag.objects.filter(tag_id=request.GET['id']).select_related('post__project')
    
    if request.GET['page'] == '1':
        lastmonth = date.today().month

        tag_obj = Tag.objects.filter(id=request.GET['id'])[0]
        monthly_count = {}
        for i in range(1, 7):
            if lastmonth - i <= 0:
                month = str(12 + lastmonth - i )
            else:
                month = str(lastmonth - i)
            if month not in tag_obj.monthly_count:
                monthly_count[month] = 0
            else:
                monthly_count[month] = tag_obj.monthly_count[month]

        post_list = []
        post_obj = Paginator(post_tag_obj.order_by('-id'), 5).get_page('1')
        for post in post_obj:
            post_list.append(post.post)

        like_list = dict(Like.objects.filter(user_id=user_id, post__in=post_list).values_list('post_id', 'user_id'))
        book_list = dict(BookMark.objects.filter(user_id=user_id, post__in=post_list).values_list('post_id', 'user_id'))
        new_post_tag_obj = MainloadSerializer(post_list, many=True).data
        for post in new_post_tag_obj:
            if post['user_id'] == user_id:
                post.update({"is_user":1})
            else:
                post.update({"is_user":0})
            
            if post['id'] in like_list:
                post.update({'is_liked':1})
            else:
                post.update({'is_liked':0})

            if post['id'] in book_list:
                post.update({'is_marked':1})
            else:
                post.update({'is_marked':0})

        post_list = []
        post_obj = Paginator(post_tag_obj.order_by('-post__like_count'), 5).get_page('1')
        for post in post_obj:
            post_list.append(post.post)
        
        like_list = dict(Like.objects.filter(user_id=user_id, post__in=post_list).values_list('post_id', 'user_id'))
        book_list = dict(BookMark.objects.filter(user_id=user_id, post__in=post_list).values_list('post_id', 'user_id'))
        pop_post_tag_obj = MainloadSerializer(post_list, many=True).data
        for post in pop_post_tag_obj:
            if post['user_id'] == user_id:
                post.update({"is_user":1})
            else:
                post.update({"is_user":0})
            
            if post['id'] in like_list:
                post.update({'is_liked':1})
            else:
                post.update({'is_liked':0})

            if post['id'] in book_list:
                post.update({'is_marked':1})
            else:
                post.update({'is_marked':0})
        
        return Response({'monthly_count':monthly_count,
                        'related_new':new_post_tag_obj,
                        'related_pop':pop_post_tag_obj}, status=status.HTTP_200_OK)
    else:
        post_list = []

        if request.GET['type'] == 'new':
            post_obj = Paginator(post_tag_obj.order_by('-id'), 5)
            if post_obj.num_pages < int (request.GET['page']):
                return Response(status=status.HTTP_204_NO_CONTENT)

            for post in post_obj.get_page(request.GET['page']):
                post_list.append(post.post)

            like_list = dict(Like.objects.filter(user_id=user_id, post__in=post_list).values_list('post_id', 'user_id'))
            book_list = dict(BookMark.objects.filter(user_id=user_id, post__in=post_list).values_list('post_id', 'user_id'))
            post_tag_obj = MainloadSerializer(post_list, many=True).data
            for post in post_tag_obj:
                if post['user_id'] == user_id:
                    post.update({"is_user":1})
                else:
                    post.update({"is_user":0})
                
                if post['id'] in like_list:
                    post.update({'is_liked':1})
                else:
                    post.update({'is_liked':0})

                if post['id'] in book_list:
                    post.update({'is_marked':1})
                else:
                    post.update({'is_marked':0})
            return Response({'related_new':post_tag_obj}, status=status.HTTP_200_OK)
        
        elif request.GET['type'] == 'pop':
            post_obj = Paginator(post_tag_obj.order_by('-post__like_count'), 5)
            if post_obj.num_pages < int (request.GET['page']):
                return Response(status=status.HTTP_204_NO_CONTENT)
                
            for post in post_obj.get_page(request.GET['page']):
                post_list.append(post.post)

            like_list = dict(Like.objects.filter(user_id=user_id, post__in=post_list).values_list('post_id', 'user_id'))
            book_list = dict(BookMark.objects.filter(user_id=user_id, post__in=post_list).values_list('post_id', 'user_id'))
            post_tag_obj = MainloadSerializer(post_list, many=True).data
            for post in post_tag_obj:
                if post['user_id'] == user_id:
                    post.update({"is_user":1})
                else:
                    post.update({"is_user":0})
                
                if post['id'] in like_list:
                    post.update({'is_liked':1})
                else:
                    post.update({'is_liked':0})

                if post['id'] in book_list:
                    post.update({'is_marked':1})
                else:
                    post.update({'is_marked':0})

            return Response({'related_pop':post_tag_obj}, status=status.HTTP_200_OK)

@api_view(['GET'])
@permission_classes((IsAuthenticated,))
def search_tag(request):
    return_dict = {}
    try:
        tag = Tag.objects.filter(tag=request.GET['query'])[0]
        result_list = [tag]
        # interest_list = InterestTag.objects.get_or_create(user_id=request.user.id)[0]
        # interest_list = interest_tag(interest_list, 'plus', tag.id, 20)
        # interest_list.save()
    except:
        result_list = []

    tags = Tag.objects.filter(tag__icontains=request.GET['query']).order_by('-count')[:10]
    
    for tag in tags:
        if tag not in result_list:
            result_list.append(tag)
            
    return_dict['results'] = TagSerializer(result_list, many=True).data
    return Response(return_dict, status=status.HTTP_200_OK)