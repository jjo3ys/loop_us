from django.core.paginator import Paginator

from tag.models import Profile_Tag, Project_Tag
from fcm.models import FcmToken
from fcm.push_fcm import like_fcm
from user_api.models import Profile
from user_api.serializers import SimpleProfileSerializer

from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework import status

from .serializers import PostingSerializer, PostingContentsImageSerializer, MainloadSerializer
from .models import Post, ContentsImage, Like, BookMark

from loop.models import Loopship

import random
# Create your views here.
@api_view(['POST', 'PUT', 'GET', 'DELETE'])
@permission_classes((IsAuthenticated,))
def posting(request):
    if request.method == 'POST':    
        profile_obj = Profile.objects.get(user_id=request.user.id)       
        post_obj = Post.objects.create(user_id=request.user.id, 
                                    project_id=request.GET['id'],
                                    title=request.data['title'],
                                    thumbnail=request.FILES.get('thumbnail'),
                                    department_id=profile_obj.department)


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
    
    elif request.method == 'PUT':
        post_obj = Post.objects.get(id=request.GET['id'])
        post_obj.title = request.data['title']
        post_obj.thumbnail = request.FILES.get('thumbnail')
    
    elif request.method == 'GET':
        user_id = request.user.id
        posting_idx = request.GET['id']

        try:
            post_obj = Post.objects.get(id=posting_idx)

        except Post.DoesNotExist:
            return Response('The posting isn\'t valid', status=status.HTTP_404_NOT_FOUND)

        postingSZ = PostingSerializer(post_obj)

        profile = SimpleProfileSerializer(Profile.objects.get(user_id=post_obj.user_id)).data
        return_dict = {
            'posting_info': postingSZ.data,
        }
        return_dict.update(profile)

        tag_list = []
        for tag in postingSZ.data['project']['project_tag']:
            tag_list.append(int(tag['tag_id']))

        recommend = Project_Tag.objects.filter(tag_id__in=tag_list)
        recommend_post = []

        for pj_tag in recommend:
            recommend_post_obj = Post.objects.filter(project=pj_tag.project)
            for r_p in recommend_post_obj:
                if r_p.id != post_obj.id and r_p not in recommend_post:
                    recommend_post.append(r_p)

        recommend_post = random.sample(recommend_post, min(3, len(recommend_post)))
        
        recommend_post = MainloadSerializer(recommend_post, many=True).data
        for post in recommend_post:
            post.update(SimpleProfileSerializer(Profile.objects.get(user_id=post['user_id'])).data)
            if post['user_id'] == user_id:
                post.update({"is_user":1})
            else:
                post.update({"is_user":0})

            try:
                Like.objects.get(user_id=user_id, post_id=post['id'])
                post.update({"is_liked":1})
            except:
                post.update({"is_liked":0})

            try:
                BookMark.objects.get(user_id=user_id, post_id=post['id'])
                post.update({"is_marked":1})
            except:
                post.update({"is_marked":0})

        return_dict.update({"recommend_post":recommend_post})

        if user_id == post_obj.user_id:
            return_dict.update({"is_user":1})
        else:
            return_dict.update({"is_user":0})

        try:
            Like.objects.get(user_id=user_id, post_id=posting_idx)
            return_dict.update({"is_liked":1})
        except:
            return_dict.update({"is_liked":0})

        try:
            BookMark.objects.get(user_id=user_id, post_id=posting_idx)
            return_dict.update({"is_marked":1})
        except:
            return_dict.update({"is_marked":0})

        return Response(return_dict)
    
    elif request.method == 'DELETE':
        post_obj = Post.objects.get(id=request.GET['id'])
        post_obj.delete()
        return Response("delete posting", status=status.HTTP_200_OK)

@api_view(['POST', ])
@permission_classes((IsAuthenticated,))
def like(request, idx):
    like_obj, valid = Like.objects.get_or_create(post_id=idx, user_id=request.user.id)
    if not valid:
        like_obj.delete()
        return Response('disliked posting', status=status.HTTP_202_ACCEPTED)
    else:
        try:
            token = FcmToken.objects.get(user_id=like_obj.post.user_id)
            real_name = Profile.objects.get(user_id=request.user.id).real_name
            like_fcm(token.token, real_name)
        except:
            pass

        return Response('liked posting', status=status.HTTP_202_ACCEPTED)

@api_view(['POST', ])
@permission_classes((IsAuthenticated,))
def bookmark(request, idx):
    book_obj, valid = BookMark.objects.get_or_create(post_id=idx, user_id=request.user.id)
    if not valid:
        book_obj.delete()
        return Response('unmarked posting', status=status.HTTP_202_ACCEPTED)
    else:
        return Response('marked posting', status=status.HTTP_202_ACCEPTED)

@api_view(['GET', ])
@permission_classes((IsAuthenticated,))
def bookmark_list_load(request):
    user = request.user
    bookmark_list = BookMark.objects.filter(user_id=user.id)
    post_obj = []
    for bookmark in bookmark_list:
        post_obj.append(bookmark.post)
    post_obj.reverse()
    post_obj = Paginator(post_obj, 5).get_page(request.GET['page'])
    post_obj = MainloadSerializer(post_obj, many=True).data

    for p in post_obj:
        p.update(SimpleProfileSerializer(Profile.objects.get(user_id=p['user_id'])).data)
        try:
            Like.objects.get(user_id=request.user.id, post_id=p['id'])
            p.update({"is_liked":1})
        except:
            p.update({"is_liked":0})
        
        p.update({"is_marked":1,
                  "is_user":1})

    return Response(post_obj, status=status.HTTP_200_OK)

@api_view(['GET', ])
@permission_classes((IsAuthenticated,))
def recommend_load(request):
    profile = Profile.objects.get(user_id=request.user.id)
    tags = Profile_Tag.objects.filter(profile_id=profile.id)
    tag_list = []
    for tag in tags:
        tag_list.append(tag.tag.id)

    projects = Project_Tag.objects.filter(tag_id__in=tag_list)
    project_list = []
    for project in projects:
        project_list.append(project.project.id)

    if request.GET['last'] == '0':
        post_obj = Post.objects.filter(department_id=profile.department)
        post_obj.union(Post.objects.exclude(department_id=profile.department).filter(project_id__in = project_list))
        post_obj = list(post_obj)[-5:]
    else:
        post_obj = Post.objects.filter(department_id=profile.department, id__lt=request.GET['last'])
        post_obj.union(Post.objects.exclude(department_id=profile.department).filter(id__lt=request.GET['last'], project_id__in = project_list))
        post_obj = list(post_obj)[-5:]
        
    post_obj.reverse()
    post_obj = MainloadSerializer(post_obj, many=True).data
    for p in post_obj:
        p.update(SimpleProfileSerializer(Profile.objects.get(user=p['user_id'])).data)
        if p['user_id'] == request.user.id:
            p.update({"is_user":1})
        else:
            p.update({"is_user":0})

        try:
            Like.objects.get(user_id=request.user.id, post_id=p['id'])
            p.update({"is_liked":1})
        except:
            p.update({"is_liked":0})

        try:
            BookMark.objects.get(user_id=request.user.id, post_id=p['id'])
            p.update({"is_marked":1})
        except:
            p.update({"is_marked":0})
    return Response(post_obj, status=status.HTTP_200_OK)
    
@api_view(['GET', ])
@permission_classes((IsAuthenticated,))
def main_load(request):
    if request.GET['last'] == '0':
        post_obj = list(Post.objects.all())[-5:]
    else:
        post_obj = list(Post.objects.filter(id__lt=request.GET['last']))[-5:]

    post_obj.reverse()
    post_obj = MainloadSerializer(post_obj, many=True).data
    for p in post_obj:
        p.update(SimpleProfileSerializer(Profile.objects.get(user=p['user_id'])).data)
        if p['user_id'] == request.user.id:
            p.update({"is_user":1})
        else:
            p.update({"is_user":0})

        try:
            Like.objects.get(user_id=request.user.id, post_id=p['id'])
            p.update({"is_liked":1})
        except:
            p.update({"is_liked":0})

        try:
            BookMark.objects.get(user_id=request.user.id, post_id=p['id'])
            p.update({"is_marked":1})
        except:
            p.update({"is_marked":0})

    return Response(post_obj, status=status.HTTP_200_OK)

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
    post_obj = MainloadSerializer(post_obj, many=True).data
    for p in post_obj:
        p.update(SimpleProfileSerializer(Profile.objects.get(user=p['user_id'])).data)
        if p['user_id'] == request.user.id:
            p.update({"is_user":1})
        else:
            p.update({"is_user":0})

        try:
            Like.objects.get(user_id=request.user.id, post_id=p['id'])
            p.update({"is_liked":1})
        except:
            p.update({"is_liked":0})

        try:
            BookMark.objects.get(user_id=request.user.id, post_id=p['id'])
            p.update({"is_marked":1})
        except:
            p.update({"is_marked":0})

    return Response(post_obj, status=status.HTTP_200_OK)

@api_view(['GET', ])
@permission_classes((IsAuthenticated,))
def like_list_load(request, idx):
    like_obj = Like.objects.filter(post_id=idx)
    like_list = []
    for l in like_obj:
       like_list.append(Profile.objects.get(user_id=l.user_id))
    
    return Response(SimpleProfileSerializer(like_list, many=True).data, status=status.HTTP_200_OK)