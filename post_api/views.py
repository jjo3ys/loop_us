from django.shortcuts import render
from django.db.models import Q
from django.core.paginator import Paginator

from user_api.models import Profile
from user_api.serializers import SimpleProfileSerializer as ProfileSerializer

from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework import status
import json

from .serializers import PostingSerializer, PostingContentsImageSerializer, LikeSerializer, MainloadSerializer
from .models import Post, ContentsImage, Like, BookMark

from loop.models import Loopship

# Create your views here.
@api_view(['POST', ])
@permission_classes((IsAuthenticated,))
def posting_upload(request, proj_idx):
    post_obj = Post.objects.create(user_id=request.user.id, 
                                   project_id=proj_idx,
                                   title=request.data['title'],
                                   thumbnail=request.FILES.get('thumbnail'))


    for image in request.FILES.getlist('image'):
        ContentsImage.objects.create(post_id=post_obj.id,
                                     image=image)

    images = PostingContentsImageSerializer(ContentsImage.objects.filter(post_id=post_obj.id), many=True).data
    image_id = 0
    contents = []
    true = True
    for d in eval(request.data['contents']):
        if type(d['insert']) == dict:
            d['insert'] = {"image":images[image_id]['image']}
            image_id += 1

        contents.append(d)

    post_obj.contents = str(contents)
    post_obj.save()

    return Response(PostingSerializer(post_obj).data, status=status.HTTP_200_OK)

@api_view(['POST', ])
@permission_classes((IsAuthenticated,))
def specific_posting_update(request, posting_idx):
    post_obj = Post.objects.get(id=posting_idx)
    post_obj.title = request.data['title']
    post_obj.thumbnail = request.FILES.get('thumbnail')



@api_view(['POST', ])
@permission_classes((IsAuthenticated,))
def like(request, idx):
    try:
        like_valid = Like.objects.get(post_id=idx, user_id=request.user.id)
        like_valid.delete()
        return Response('disliked posting', status=status.HTTP_202_ACCEPTED)
    except:
        Like.objects.create(post_id=idx, user_id=request.user.id)
        return Response('liked posting', status=status.HTTP_202_ACCEPTED)

@api_view(['POST', ])
@permission_classes((IsAuthenticated,))
def bookmark(request, idx):
    try:
        book_obj = BookMark.objects.get(post_id=idx, user_id=request.user.id)
        book_obj.delete()
        return Response('unmarked posting', status=status.HTTP_202_ACCEPTED)
    except:
        BookMark.objects.create(post_id=idx, user_id=request.user.id)
        return Response('marked posting', status=status.HTTP_202_ACCEPTED)

@api_view(['GET', ])
@permission_classes((IsAuthenticated,))
def main_load(request):
    post_obj = Post.objects.all().order_by('-id')
    post_obj = Paginator(post_obj, 5).get_page(request.GET['page'])
    post = MainloadSerializer(post_obj, many=True).data

    for d in post:
        try:
            Like.objects.get(user_id=request.user.id, post_id=d['id'])
            d.update({"is_liked":1})
        except:
            pass

        try:
            BookMark.objects.get(user_id=request.user.id, post_id=d['id'])
            d.update({"is_marked":1})
        except:
            pass

    return Response(post, status=status.HTTP_200_OK)

@api_view(['GET', ])
@permission_classes((IsAuthenticated,))
def loop_load(request):
    loop = list(Loopship.objects.filter(user_id=request.user.id))

    loop_list = []
    for l in loop:
        loop_list.append(l.friend_id)

    post_obj = Post.objects.filter(user_id__in=loop_list).order_by('-id')
    data = MainloadSerializer(post_obj, many=True).data
    for d in data:
        try:
            Like.objects.get(user_id=request.user.id, post_id=d['id'])
            d.update({"is_liked":1})
        except:
            pass

        try:
            BookMark.objects.get(user_id=request.user.id, post_id=d['id'])
            d.update({"is_marked":1})
        except:
            pass

    return Response(data, status=status.HTTP_200_OK)

@api_view(['GET', ])
@permission_classes((IsAuthenticated,))
def posting_list_load(request, proj_idx):
    try:
        postings = Post.objects.filter(project=proj_idx)    
    except Post.DoesNotExist:
        return Response('The postings aren\'t valid', status=status.HTTP_404_NOT_FOUND)

    posting = PostingSerializer(postings, many=True).data

    return Response(posting, status=status.HTTP_200_OK)

@api_view(['GET', ])
@permission_classes((IsAuthenticated,))
def specific_posting_load(request, posting_idx):
    user_id = request.user.id
    try:
        post_obj = Post.objects.get(id=posting_idx)

    except Post.DoesNotExist:
        return Response('The posting isn\'t valid', status=status.HTTP_404_NOT_FOUND)

    postingSZ = PostingSerializer(post_obj)

    profile_obj = Profile.objects.get(user_id=post_obj.user_id)
    profile = ProfileSerializer(profile_obj).data
    return_dict = {
        'posting_info': postingSZ.data,
    }
    return_dict.update(profile)
    if user_id == post_obj.user_id:
        return_dict.update({"is_user":1})

    return Response(return_dict)

@api_view(['GET', ])
@permission_classes((IsAuthenticated,))
def like_list_load(request, idx):
    like_obj = Like.objects.filter(post_id=idx)
    like_list = []
    for l in like_obj:
       like_list.append(Profile.objects.get(user_id=l.user_id))
    
    return Response(ProfileSerializer(like_list, many=True).data, status=status.HTTP_200_OK)
        

@api_view(['GET', ])
@permission_classes((IsAuthenticated,))
def posting_delete(request, idx):
    post_obj = Post.objects.get(id=idx)
    post_obj.delete()

    return Response("delete posting", status=status.HTTP_200_OK)