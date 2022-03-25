from django.core.paginator import Paginator
from search.models import Get_log, InterestTag
from search.views import interest_tag

from tag.models import Post_Tag, Tag
from fcm.models import FcmToken
from fcm.push_fcm import like_fcm, report_alarm
from user_api.models import Banlist, Profile, Report
from user_api.serializers import SimpleProfileSerializer

from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework import status

from .serializers import PostingSerializer, MainloadSerializer
from .models import Post, PostImage, Like, BookMark

from loop.models import Loopship

import random
import datetime
# Create your views here.
@api_view(['POST', 'PUT', 'GET', 'DELETE'])
@permission_classes((IsAuthenticated,))
def posting(request):
    if request.method == 'POST':    
        profile_obj = Profile.objects.get(user_id=request.user.id)       
        post_obj = Post.objects.create(user_id=request.user.id, 
                                        project_id=request.GET['id'],    
                                        contents=request.GET['contents'],
                                        department_id=profile_obj.department)


        for image in request.FILES.getlist('image'):
            PostImage.objects.create(post_id=post_obj.id,
                                     image=image)

        interest_list = InterestTag.objects.get_or_create(user_id=request.user.id)[0]
        for tag in eval(request.data['tag']):
            tag_obj, created = Tag.objects.get_or_create(tag=tag)
            interest_tag(interest_list, 'plus', tag_obj.id, 10)
            if not created:
                tag_obj.count += 1
                tag_obj.save()
            Post_Tag.objects.create(post=post_obj, tag=tag_obj)
        
        interest_list.save()
        return Response(post_obj, status=status.HTTP_200_OK)
    
    elif request.method == 'PUT':
        post_obj = Post.objects.get(id=request.GET['id'])
        
        if request.GET['type'] == 'image':
            pass
        
        elif request.GET['type'] == 'contents':
            post_obj.contents = request.data['contents']
        
        elif request.GET['type'] == 'tag':
            interest_list = InterestTag.objects.get_or_create(user_id=request.user.id)[0]
            tag_obj = Post_Tag.objects.filter(post_id=post_obj.id)
            for tag in tag_obj:
                interest_list = interest_tag(interest_list, 'minus', tag.tag_id, 10)
                tag.delete()
                tag.tag.count = tag.tag.count-1
                if tag.tag.count == 0:
                    tag.tag.delete()
                tag.tag.save()

            tag_list = eval(request.data['tag'])      
            for tag in tag_list:
                tag_obj, created = Tag.objects.get_or_create(tag=tag)
                Post_Tag.objects.create(tag = tag_obj, post_id = post_obj.id)
                interest_list = interest_tag(interest_list, 'plus', tag_obj.id, 10)

                if not created:
                    tag_obj.count = tag_obj.count+1
                    tag_obj.save()    

            interest_list.save()

        post_obj.save()
        return Response(status=status.HTTP_200_OK)
    
    elif request.method == 'GET':
        user_id = request.user.id
        posting_idx = request.GET['id']

        try:
            post_obj = Post.objects.get(id=posting_idx)

        except Post.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)

        postingSZ = PostingSerializer(post_obj)

        return_dict = {
            'posting_info': postingSZ.data,
        }

        tag_list = []
        for tag in postingSZ.data['project']['project_tag']:
            tag_list.append(int(tag['tag_id']))

        post_tag = Post_Tag.objects.filter(tag_id__in=tag_list)
        recommend_post = []

        for recommend in post_tag:
            if recommend.post_id != post_obj.id and recommend.post not in recommend_post:
                recommend_post.append(recommend.post)

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
            Get_log.objects.create(user_id=user_id, target_id=posting_idx, type=4)
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
        contents_image_obj = PostImage.objects.filter(post_id=post_obj.id)
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
    tags = InterestTag.objects.get(user_id=request.user.id).tag_list
    try:
        ban_list = Banlist.objects.get(user_id=request.user.id).banlist
    except:
        ban_list = []

    ban_list += Banlist.objects.filter(banlist__contains=request.user.id).values_list('user_id', flat=True)

    tag_score = {}
    for post in Post_Tag.objects.filter(tag_id__in=tags):
        try:
            tag_score[post.post_id] += tags[str(post.tag_id)]['count']
        except KeyError:
            tag_score[post.post_id] = tags[str(post.tag_id)]['count']

    today = datetime.date.today()

    post_list = []
    for post in Post.objects.filter(date__range=[today-datetime.timedelta(days=7), datetime.datetime.now()]).exclude(user_id__in=ban_list):
        try:
            post_list.append([post, tag_score[post.project_id]])
        except KeyError:
            pass

    post_list.sort(key=lambda x: (-x[1], -x[0].id))
    page = int(request.GET['page'])
    post_obj = MainloadSerializer([x[0] for x in post_list[5*(page-1):5*page]], many=True).data
    post_list = 0

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
    try:
        ban_list = Banlist.objects.get(user_id=request.user.id).banlist
    except:
        ban_list = []

    ban_list += Banlist.objects.filter(banlist__contains=request.user.id).values_list('user_id', flat=True)

    if request.GET['last'] == '0':
        post_obj = list(Post.objects.all().exclude(user_id__in=ban_list))[-5:]
    else:
        post_obj = list(Post.objects.filter(id__lt=request.GET['last']).exclude(user_id__in=ban_list))[-5:]

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
    Report.objects.create(user_id=request.user.id, type=1, target_id=request.data['id'], reason=request.data['reason'])
    count = Report.objects.filter(type=1, target_id=request.data['id']).count()
    if count >= 3:
        report_alarm(count, 1, request.data['id'], request.data['reason'])
    return Response(status=status.HTTP_200_OK)