from django.core.paginator import Paginator
from project_api.models import TagLooper
from search.models import InterestTag

from tag.models import Profile_Tag, Project_Tag
from fcm.models import FcmToken
from fcm.push_fcm import like_fcm, report_alarm
from user_api.models import Profile, Report
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
            if d['type'] == 'IMAGE' and d['content'] == 'image':
                d['content'] = images[image_id]['image']
                image_id += 1

            contents.append(d)

        post_obj.contents = str(contents)
        post_obj.save()
        post_obj = MainloadSerializer(post_obj).data
        return Response(post_obj, status=status.HTTP_200_OK)
    
    elif request.method == 'PUT':
        post_obj = Post.objects.get(id=request.GET['id'])
        if request.GET['type'] == 'title':
            post_obj.title = request.data['title']
        
        elif request.GET['type'] == 'thumbnail':
            post_obj.thumbnail.delete(save=False)
            post_obj.thumbnail = request.FILES.get('thumbnail')
        
        elif request.GET['type'] == 'contents':
            image_objs = ContentsImage.objects.filter(post_id=request.GET['id'])

            for image in image_objs:
                if image.image.url not in post_obj.contents:
                    image.image.delete(save=False)
                    image.delete()

            image_list = []
            for image in request.FILES.getlist('image'):
                image_obj = ContentsImage.objects.create(post_id=request.GET['id'], image=image)
                image_list.append(image_obj.image.url)

            image_id = 0
            contents = []
            for content in eval(request.data['contents']):
                if content['type'] == 'IMAGE' and content['content'] == 'image':
                    content['content'] = image_list[image_id]
                    image_id += 1
                contents.append(content)
            
            post_obj.contents = str(contents)
        
        post_obj.save()
        return Response('Update OK', status=status.HTTP_200_OK)
    
    elif request.method == 'GET':
        user_id = request.user.id
        posting_idx = request.GET['id']

        try:
            post_obj = Post.objects.get(id=posting_idx)

        except Post.DoesNotExist:
            return Response('The posting isn\'t valid', status=status.HTTP_404_NOT_FOUND)

        postingSZ = PostingSerializer(post_obj)

        return_dict = {
            'posting_info': postingSZ.data,
        }

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
        post_obj.thumbnail.delete(save=False)
        contents_image_obj = ContentsImage.objects.filter(post_id=post_obj.id)
        for image in contents_image_obj:
            image.image.delete(save=False)
        post_obj.delete()
        return Response("delete posting", status=status.HTTP_200_OK)

@api_view(['POST', ])
@permission_classes((IsAuthenticated,))
def like(request, idx):
    try:
        like_obj, valid = Like.objects.get_or_create(post_id=idx, user_id=request.user.id)
    except:
        return Response(status=status.HTTP_404_NOT_FOUND)

    if not valid:
        like_obj.delete()
        return Response('disliked posting', status=status.HTTP_202_ACCEPTED)
    else:
        if like_obj.post.user_id != request.user.id:
            try:
                token = FcmToken.objects.get(user_id=like_obj.post.user_id)
                real_name = Profile.objects.get(user_id=request.user.id).real_name
                like_fcm(token, real_name, idx, request.user.id)
            except:
                pass

        return Response('liked posting', status=status.HTTP_202_ACCEPTED)

@api_view(['POST', ])
@permission_classes((IsAuthenticated,))
def bookmark(request, idx):
    try:
        book_obj, valid = BookMark.objects.get_or_create(post_id=idx, user_id=request.user.id)
    except:
        return Response(status=status.HTTP_404_NOT_FOUND)

    if not valid:
        book_obj.delete()
        return Response('unmarked posting', status=status.HTTP_202_ACCEPTED)
    else:
        return Response('marked posting', status=status.HTTP_202_ACCEPTED)

@api_view(['GET', ])
@permission_classes((IsAuthenticated,))
def bookmark_list_load(request):
    user = request.user
    bookmark_list = BookMark.objects.filter(user_id=user.id).order_by('-id')
    bookmark_list = Paginator(bookmark_list, 10).get_page(request.GET['page'])
    post_obj = []
    for bookmark in bookmark_list:
        post_obj.append(bookmark.post)

    post_obj = MainloadSerializer(post_obj, many=True).data

    for p in post_obj:
        if Like.objects.filter(user_id=request.user.id, post_id=p['id']).exists():
            p.update({"is_liked":1})
        else:
            p.update({"is_liked":0})
        
        p.update({"is_marked":1,
                  "is_user":1})

    return Response(post_obj, status=status.HTTP_200_OK)

@api_view(['GET', ])
@permission_classes((IsAuthenticated,))
def recommend_load(request):
    profile = Profile.objects.get(user_id=request.user.id)
    tag_list = []

    try:
        tags = InterestTag.objects.get(user_id=request.user.id).tag_list
        tags = sorted(tags.items(), key = lambda x:(x[1]['date'], x[1]['count']), reverse=True)
        for tag in tags:
            tag_list.append(tag[1]['id'])

    except InterestTag.DoesNotExist:
        tags = Profile_Tag.objects.filter(profile_id=profile.id)
        for tag in tags:
            tag_list.append(tag.tag.id)

    projects = Project_Tag.objects.filter(tag_id__in=tag_list)
    project_list = []
    for project in projects:
        project_list.append(project.project.id)

    if request.GET['last'] == '0':
        post_obj = Post.objects.filter(project_id__in = project_list)

    else:
        post_obj = Post.objects.filter(project_id__in = project_list, id__lt=request.GET['last'])

    post_obj = MainloadSerializer(reversed(list(post_obj)[-5:]), many=True).data
    for p in post_obj:
        if p['user_id'] == request.user.id:
            p.update({"is_user":1})
        else:
            p.update({"is_user":0})

        
        if Like.objects.filter(user_id=request.user.id, post_id=p['id']).exists():
            p.update({"is_liked":1})
        else:
            p.update({"is_liked":0})

        
        if BookMark.objects.filter(user_id=request.user.id, post_id=p['id']).exists():
            p.update({"is_marked":1})
        else:
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
        if p['user_id'] == request.user.id:
            p.update({"is_user":1})
        else:
            p.update({"is_user":0})

        if Like.objects.filter(user_id=request.user.id, post_id=p['id']).exists():
            p.update({"is_liked":1})
        else:
            p.update({"is_liked":0})

        
        if BookMark.objects.filter(user_id=request.user.id, post_id=p['id']).exists():
            p.update({"is_marked":1})
        else:
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
        if p['user_id'] == request.user.id:
            p.update({"is_user":1})
        else:
            p.update({"is_user":0})

        if Like.objects.filter(user_id=request.user.id, post_id=p['id']).exists():
            p.update({"is_liked":1})
        else:
            p.update({"is_liked":0})

        
        if BookMark.objects.filter(user_id=request.user.id, post_id=p['id']).exists():
            p.update({"is_marked":1})
        else:
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

@api_view(['POST'])
@permission_classes((IsAuthenticated,))
def report_posting(request):
    Report.objects.create(user_id=request.user.id, type=False, target_id=request.data['id'], reason=request.data['reason'])
    count = Report.objects.filter(type=False, target_id=request.data['id']).count()
    if count >= 3:
        report_alarm(count, False, request.data['id'], request.data['reason'])
    return Response(status=status.HTTP_200_OK)