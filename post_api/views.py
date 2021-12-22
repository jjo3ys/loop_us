from django.shortcuts import render
from user_api.models import Profile
from user_api.serializers import SimpleProfileSerializer as ProfileSerializer

from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework import status
import json

from .serializers import PostingSerializer, PostingContentsImageSerializer, LikeSerializer

from .models import Post, ContentsImage, Like


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
    
    for d in json.loads(request.data['contents']):
        if type(d['insert']) == dict:
            d['insert'] = {"image":images[image_id]['image']}
            image_id += 1
        contents.append(d)

    post_obj.contents = contents
    post_obj.save()

    return Response(PostingSerializer(post_obj).data, status=status.HTTP_200_OK)

@api_view(['GET', ])
@permission_classes((IsAuthenticated,))
def posting_list_load(request, proj_idx):
    try:
        postings = Post.objects.filter(project=proj_idx)    
    except Post.DoesNotExist:
        return Response('The postings aren\'t valid', status=status.HTTP_404_NOT_FOUND)

    postingSZ = PostingSerializer(postings, many=True)

    return_dict = {
        'posting_list' : postingSZ.data
    }

    for posting in return_dict['posting_list']:
        posting.update({'like_num': len(posting['like'])})
    return Response(return_dict)

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

@api_view(['POST', ])
@permission_classes((IsAuthenticated,))
def specific_posting_update(request, posting_idx):
    post_obj = Post.objects.get(id=posting_idx)
    post_obj.title = request.data['title']
    post_obj.thumbnail = request.FILES.get('thumbnail')



@api_view(['POST', ])
@permission_classes((IsAuthenticated,))
def like(request, type, idx):

    if type == 'posting':
        try:
            like_valid = Like.objects.get(posting=idx, user=request.user.id)
            like_valid.delete()
            return Response('disliked posting', status=status.HTTP_202_ACCEPTED)
        except:
            Like.objects.create(posting=idx, user=request.user.id)
            return Response('liked posting', status=status.HTTP_202_ACCEPTED)