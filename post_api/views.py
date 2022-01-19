from django.core.paginator import Paginator
from django.db.models import Q

from tag.models import Project_Tag
from fcm.models import FcmToken
from fcm.push_fcm import like_fcm
from user_api.models import Profile
from user_api.serializers import SimpleProfileSerializer as ProfileSerializer

from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework import status

from .serializers import PostingSerializer, PostingContentsImageSerializer, MainloadSerializer, SimpleProjectserializer
from .models import Post, ContentsImage, Like, BookMark

from loop.models import Loopship

import random
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

    for d in eval(request.data['contents']):
        if d['content'] == 'image':
            d['content'] = images[image_id]['image']
            image_id += 1

        contents.append(d)

    post_obj.contents = str(contents)
    post_obj.save()

    return Response("ok", status=status.HTTP_200_OK)

@api_view(['POST', ])
@permission_classes((IsAuthenticated,))
def specific_posting_update(request, posting_idx):
    post_obj = Post.objects.get(id=posting_idx)
    post_obj.title = request.data['title']
    post_obj.thumbnail = request.FILES.get('thumbnail')

@api_view(['POST', ])
@permission_classes((IsAuthenticated,))
def like(request, idx):
    like, valid = Like.objects.get_or_create(post_id=idx, user_id=request.user.id)
    if not valid:
        like.delete()
        return Response('disliked posting', status=status.HTTP_202_ACCEPTED)
    else:
        try:
            token = FcmToken.objects.get(user_id=like.post.user_id)
            real_name = Profile.objects.get(user_id=request.user.id).real_name
            like_fcm(token.token, real_name)
        except:
            pass

        return Response('liked posting', status=status.HTTP_202_ACCEPTED)

@api_view(['POST', ])
@permission_classes((IsAuthenticated,))
def bookmark(request, idx):
    book, valid = BookMark.objects.get_or_create(post_id=idx, user_id=request.user.id)
    if not valid:
        book.delete()
        return Response('unmarked posting', status=status.HTTP_202_ACCEPTED)
    else:
        return Response('marked posting', status=status.HTTP_202_ACCEPTED)

@api_view(['GET', ])
@permission_classes((IsAuthenticated,))
def bookmark_list_load(request):
    user = request.user
    bookmark_list = BookMark.objects.filter(user_id=user.id)
    post_list = []
    for bookmark in bookmark_list:
        post_list.append(bookmark.post)

    post_obj = Paginator(post_list, 5).get_page(request.GET['page'])
    post = MainloadSerializer(post_obj, many=True).data

    for i in range(len(post_obj)):
        profile_obj = Profile.objects.get(user=post_obj[i].user)
        post[i].update(SimpleProjectserializer(post_obj[i].project).data)    
        post[i].update(ProfileSerializer(profile_obj).data)
        try:
            Like.objects.get(user_id=request.user.id, post_id=post_obj[i].id)
            post[i].update({"is_liked":1})
        except:
            post[i].update({"is_liked":0})
        post[i].update({"is_marked":1,
                        "is_user":1})

    return Response(post, status=status.HTTP_200_OK)

@api_view(['GET', ])
@permission_classes((IsAuthenticated,))
def main_load(request):
    if request.GET['last'] == '0':
        post_obj = list(Post.objects.all())[-5:]
    else:
        post_obj = list(Post.objects.filter(id__lt=request.GET['last']))[-5:]

    post_obj.reverse()
    post = MainloadSerializer(post_obj, many=True).data

    for i in range(len(post_obj)):
        profile_obj = Profile.objects.get(user=post_obj[i].user)
        post[i].update(SimpleProjectserializer(post_obj[i].project).data)    
        post[i].update(ProfileSerializer(profile_obj).data)
        if post_obj[i].user.id == request.user.id:
            post[i].update({"is_user":1})
        else:
            post[i].update({"is_user":0})

        try:
            Like.objects.get(user_id=request.user.id, post_id=post_obj[i].id)
            post[i].update({"is_liked":1})
        except:
            post[i].update({"is_liked":0})

        try:
            BookMark.objects.get(user_id=request.user.id, post_id=post_obj[i].id)
            post[i].update({"is_marked":1})
        except:
            post[i].update({"is_marked":0})

    return Response(post, status=status.HTTP_200_OK)

@api_view(['GET', ])
@permission_classes((IsAuthenticated,))
def loop_load(request):
    loop = list(Loopship.objects.filter(user_id=request.user.id))

    loop_list = []
    for l in loop:
        loop_list.append(l.friend_id)

    if request.GET['last'] == '0':
        post_obj = list(Post.objects.filter(user_id__in=loop_list))[-5:]
    else:
        post_obj = list(Post.objects.filter(id__lt=request.GET['last'], user_id__in=loop_list))[-5:]

    post_obj.reverse()
    post = MainloadSerializer(post_obj, many=True).data
    for i in range(len(post_obj)):
        profile_obj = Profile.objects.get(user=post_obj[i].user)
        post[i].update(SimpleProjectserializer(post_obj[i].project).data)    
        post[i].update(ProfileSerializer(profile_obj).data)
        if post_obj[i].user.id == request.user.id:
            post[i].update({"is_user":1})
        else:
            post[i].update({"is_user":0})

        try:
            Like.objects.get(user_id=request.user.id, post_id=post_obj[i].id)
            post[i].update({"is_liked":1})
        except:
            post[i].update({"is_liked":0})

        try:
            BookMark.objects.get(user_id=request.user.id, post_id=post_obj[i].id)
            post[i].update({"is_marked":1})
        except:
            post[i].update({"is_marked":0})

    return Response(post, status=status.HTTP_200_OK)


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
    project = SimpleProjectserializer(post_obj.project).data
    return_dict = {
        'posting_info': postingSZ.data,
    }
    return_dict.update(profile)
    return_dict.update(project)

    tag_list = []
    for tag in project['project_tag']:
        tag_list.append(int(tag['tag_id']))

    recommend = Project_Tag.objects.filter(tag_id__in=tag_list)
    recommend_post = []

    for pj_tag in recommend:
        post = Post.objects.filter(project=pj_tag.project)
        for p in post:
            if p.id != post_obj.id and p not in recommend_post:
                recommend_post.append(p)

    recommend_post = random.sample(recommend_post, min(3, len(recommend_post)))
    
    recommend_post = MainloadSerializer(recommend_post, many=True).data
    return_dict.update({"recommend_post":recommend_post})

    if user_id == post_obj.user_id:
        return_dict.update({"is_user":1})
    else:
        return_dict.update({"is_user":0})

    try:
        Like.objects.get(user_id=request.user.id, post_id=posting_idx)
        return_dict.update({"is_liked":1})
    except:
        return_dict.update({"is_liked":0})

    try:
        BookMark.objects.get(user_id=request.user.id, post_id=posting_idx)
        return_dict.update({"is_marked":1})
    except:
        return_dict.update({"is_marked":0})
    return Response(return_dict)

@api_view(['GET', ])
@permission_classes((IsAuthenticated,))
def like_list_load(request, idx):
    like_obj = Like.objects.filter(post_id=idx)
    like_list = []
    for l in like_obj:
       like_list.append(Profile.objects.get(user_id=l.user_id))
    
    return Response(ProfileSerializer(like_list, many=True).data, status=status.HTTP_200_OK)
        

@api_view(['POST', ])
@permission_classes((IsAuthenticated,))
def posting_delete(request, idx):
    post_obj = Post.objects.get(id=idx)
    post_obj.delete()
    return Response("delete posting", status=status.HTTP_200_OK)