from genericpath import exists
from django.core.paginator import Paginator
from crawling_api.models import News
from project_api.models import Project
from search.models import Get_log, InterestTag
from search.views import interest_tag

from tag.models import Post_Tag, Tag
from fcm.models import FcmToken
from fcm.push_fcm import like_fcm, report_alarm, comment_like_fcm
from user_api.models import Banlist, Profile, Report
from user_api.serializers import SimpleProfileSerializer

from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework import status

from .serializers import CocommentSerializer, CommentSerializer, NewsSerializer, PostingSerializer, MainloadSerializer
from .models import CocommentLike, CommentLike, Post, PostImage, Like, BookMark, Cocomment, Comment, PostLink

from loop.models import Loopship

import random
import datetime
# Create your views here.
@api_view(['POST', 'PUT', 'GET', 'DELETE'])
@permission_classes((IsAuthenticated,))
def posting(request):
    if request.method == 'POST': 
        profile_obj = Profile.objects.filter(user_id=request.user.id)[0]
        post_obj = Post.objects.create(user_id=request.user.id, 
                                        project_id=request.GET['id'],    
                                        contents=request.data['contents'],
                                        department_id=profile_obj.department)
        project_obj = Project.objects.filter(id=request.GET['id'])[0]
        project_obj.post_count += 1

        for image in request.FILES.getlist('image'):
            PostImage.objects.create(post_id=post_obj.id,
                                     image=image)

        project_group = project_obj.group
        
        interest_list = InterestTag.objects.get_or_create(user_id=request.user.id)[0]

        for link in request.data.getlist('link'):
            PostLink.objects.create(post_id=post_obj.id, link=link)

        for tag in request.data.getlist('tag'):
            tag_obj, created = Tag.objects.get_or_create(tag=tag)
            interest_tag(interest_list, 'plus', tag_obj.id, 10)
            if not created:
                tag_obj.count += 1
                tag_obj.save()

            elif created: continue

            if str(tag_obj.group_id) in project_group:
                project_group[str(tag_obj.group_id)] += 1
            else:
                project_group[str(tag_obj.group_id)] = 1

            Post_Tag.objects.create(post=post_obj, tag=tag_obj)

        project_obj.group = project_group
        project_obj.save()

        project_obj = Project.objects.filter(user_id=request.user.id)
        for project in project_obj:
            if project.group == None:
                continue

            group = [k for k, v in project.group.items() if max(project.group.values())==v]
            for g in group:
                if g in project_group:
                    project_group[g] += 1
                else:
                    project_group[g] = 1
        if len(project_group) == 0:
            pass
        else:
            profile_obj.group = max(project_group, key=project_group.get)
            profile_obj.save()  

        interest_list.save()
        return Response(PostingSerializer(post_obj).data, status=status.HTTP_200_OK)
    
    elif request.method == 'PUT':
        post_obj = Post.objects.filter(id=request.GET['id'])[0]
        
        if request.GET['type'] == 'link':
            link_list = request.FILES.get_list('link')
            PostLink.objects.filter(post_id=post_obj.id).delete()
            
            for link in link_list:
                PostLink.objects.create(post_id=post_obj.id, link=link)
                        
        elif request.GET['type'] == 'contents':
            post_obj.contents = request.data['contents']
        
        elif request.GET['type'] == 'tag':
            profile_obj = Profile.objects.filter(user_id=request.user.id)[0]
            interest_list = InterestTag.objects.get_or_create(user_id=request.user.id)[0]
            tag_obj = Post_Tag.objects.filter(post_id=post_obj.id).select_related('tags')
            project_group = post_obj.project.group
            tag_list = request.data.getlist('tag')

            for tag in tag_obj:
                interest_list = interest_tag(interest_list, 'minus', tag.tag_id, 10)
                
                tag.tag.count = tag.tag.count-1
                if tag.tag.count == 0:
                    tag.tag.delete()
                tag.tag.save()

                if tag.tag.group in project_group:
                    project_group[tag.tag.group] -= 1
                tag.delete()

            for tag in tag_list:
                tag_obj, created = Tag.objects.get_or_create(tag=tag)
                Post_Tag.objects.create(tag = tag_obj, post_id = post_obj.id)
                interest_list = interest_tag(interest_list, 'plus', tag_obj.id, 10)

                if not created:
                    tag_obj.count = tag_obj.count+1
                    tag_obj.save()  
                elif created: continue

                if tag.tag.group in project_group:
                    project_group[tag.tag.group] += 1
                else:
                    project_group[tag.tag.group] = 1

            post_obj.project.group = project_group
            post_obj.project.save()  
            
            project_obj = Project.objects.filter(user_id=request.user_id)
            for project in project_obj:
                if project.group == None:
                    continue

                group = [k for k, v in project.group.items() if max(project.group.values())==v]
                for g in group:
                    if g in project_group:
                        project_group[g] += 1
                    else:
                        project_group[g] = 1
            if len(project_group) == 0: pass
            else:
                profile_obj.group = max(project_group, key=project_group.get)
                profile_obj.save()

            interest_list.save()

        post_obj.save()
        return Response(status=status.HTTP_200_OK)
    
    elif request.method == 'GET':
        try:
            post_obj = Post.objects.select_related('project').select_related('user').filter(id=request.GET['id'])[0]
        except Post.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)

        post_obj = PostingSerializer(post_obj).data


        if request.user.id == post_obj['user_id']:
            post_obj.update({"is_user":1})
        else:
            # Get_log.objects.create(user_id=request.user.id, target_id=request.GET['id'], type=4)
            post_obj.update({"is_user":0})

        exists = Like.objects.filter(user_id=request.user.id, post_id=request.GET['id']).exists()
        if exists:
            post_obj.update({"is_liked":1})
        else:
            post_obj.update({"is_liked":0})
        
        for comment in post_obj['comments']:
            exists = CommentLike.objects.filter(user_id=request.user.id, comment_id=comment['id']).exists()
            if exists:
                comment.update({'is_liked':1})
            else:
                comment.update({'is_liked':0})
            for cocomment in comment['cocomments']:
                exists = CocommentLike.objects.filter(user_id=request.user.id, cocomment_id=cocomment['id']).exists()
                if exists:
                    cocomment.update({'is_liked':1})
                else:
                    cocomment.update({'is_liked':0})

        exists = BookMark.objects.filter(user_id=request.user.id, post_id=request.GET['id']).exists()
        if exists:
            post_obj.update({"is_marked":1})
        else:
            post_obj.update({"is_marked":0})

        return Response(post_obj, status=status.HTTP_200_OK)
    
    elif request.method == 'DELETE':
        post_obj = Post.objects.filter(id=request.GET['id']).select_related('project')[0]
        contents_image_obj = PostImage.objects.filter(post_id=post_obj.id)
        if contents_image_obj.count() != 0:
            for image in contents_image_obj:
                image.image.delete(save=False)
        
        post_obj.project.post_count -=1
        post_obj.project.save()
        post_obj.delete()
        return Response("delete posting", status=status.HTTP_200_OK)

@api_view(['POST', 'DELETE', 'PUT'])
@permission_classes((IsAuthenticated,))
def comment(request):   
    if request.method =='POST':
        if request.GET['type'] == 'post':
            comment_obj = Comment.objects.create(user_id=request.user.id,
                                                 post_id=request.GET['id'],#포스트 id
                                                 content=request.data['content'])

            return Response(CommentSerializer(comment_obj).data,status=status.HTTP_201_CREATED)

        elif request.GET['type'] == 'comment':
            cocomment_obj = Cocomment.objects.create(user_id=request.user.id,
                                                     comment_id=request.GET['id'],#댓글 id
                                                     content=request.data['content'],
                                                     tagged_id=request.data['tagged_user'])
        
            return Response(CocommentSerializer(cocomment_obj).data, status=status.HTTP_201_CREATED)
    
    elif request.method =='PUT':
        if request.GET['type'] == 'post':
            comment_obj = Comment.objects.filter(id=request.data['id'])[0]#댓글 id
            comment_obj.content=request.data['content']
            comment_obj.save()

            return Response(CommentSerializer(comment_obj).data,status=status.HTTP_201_CREATED)

        elif request.GET['type'] == 'comment':
            cocomment_obj = Cocomment.objects.filter(id=request.data['id'])[0]#대댓글 id
            cocomment_obj.content=request.data['content']
            cocomment_obj.save()
            
            return Response(CocommentSerializer(cocomment_obj).data, status=status.HTTP_201_CREATED)
    
    elif request.method == 'DELETE':
        if request.GET['type'] == 'post':
            try:
                comment = Cocomment.objects.filter(id=request.GET['id'])[0]#댓글 id
                comment.delete()
            except:
                return Response(status=status.HTTP_404_NOT_FOUND)

        elif request.GET['type'] == 'comment':
            try:
                cocomment = Cocomment.objects.filter(id=request.data['id'])[0]#대댓글 id
                cocomment.delete()
            except:
                return Response(status=status.HTTP_404_NOT_FOUND)
        
        return Response(status=status.HTTP_200_OK)

@api_view(['POST', ])
@permission_classes((IsAuthenticated,))
def like(request):
    type = request.GET['type']
    idx = request.GET['id']
    if type =='post':
        try:
            like_obj, created = Like.objects.get_or_create(post_id=idx, user_id=request.user.id)
        except:
            return Response(status=status.HTTP_404_NOT_FOUND)

        if not created:
            like_obj.post.like_count -= 1
            like_obj.post.save()
            like_obj.delete()
            return Response('unliked posting', status=status.HTTP_202_ACCEPTED)

        else:
            like_obj.post.like_count += 1
            like_obj.post.save()
            if like_obj.post.user_id != request.user.id:
                try:
                    token = FcmToken.objects.filter(user_id=like_obj.post.user_id)[0]
                    real_name = Profile.objects.filter(user_id=request.user.id)[0].real_name
                    like_fcm(token, real_name, idx, request.user.id)
                except:
                    pass

            return Response('liked posting', status=status.HTTP_202_ACCEPTED)

    elif type =='comment':
        try:
            like_obj, created = CommentLike.objects.get_or_create(comment_id=idx, user_id=request.user.id)
        except:
            return Response(status=status.HTTP_404_NOT_FOUND)

        if not created:
            like_obj.comment.like_count -= 1
            like_obj.comment.save()
            like_obj.delete()

            return Response('unliked comment', status=status.HTTP_202_ACCEPTED)

        else:
            like_obj.comment.like_count += 1
            like_obj.comment.save()
            if like_obj.comment.user_id != request.user.id:
                try:
                    token = FcmToken.objects.filter(user_id=like_obj.post.user_id)[0]
                    real_name = Profile.objects.filter(user_id=request.user.id)[0].real_name
                    comment_like_fcm(token, real_name, idx, request.user.id)
                except:
                    pass

            return Response('liked comment', status=status.HTTP_202_ACCEPTED)  
                 
    elif type =='cocomment':
        try:
            like_obj, created = CocommentLike.objects.get_or_create(cocomment_id=idx, user_id=request.user.id)
        except:
            return Response(status=status.HTTP_404_NOT_FOUND)

        if not created:
            like_obj.cocomment.like_count -= 1
            like_obj.cocomment.save()
            like_obj.delete()
            return Response('unliked cocomment', status=status.HTTP_202_ACCEPTED)

        else:
            like_obj.cocomment.like_count += 1
            like_obj.cocomment.save()
            if like_obj.cocomment.user_id != request.user.id:
                try:
                    token = FcmToken.objects.filter(user_id=like_obj.post.user_id)[0]
                    real_name = Profile.objects.filter(user_id=request.user.id)[0].real_name
                    comment_like_fcm(token, real_name, idx, request.user.id)
                except:
                    pass

            return Response('liked cocomment', status=status.HTTP_202_ACCEPTED)    
                    
@api_view(['POST', ])
@permission_classes((IsAuthenticated,))
def bookmark(request):
    idx = request.GET['id']
    try:
        book_obj, created = BookMark.objects.get_or_create(post_id=idx, user_id=request.user.id)
    except:
        return Response(status=status.HTTP_404_NOT_FOUND)

    if not created:
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
    tags = InterestTag.objects.filter(user_id=request.user.id)[0].tag_list
    try:
        ban_list = Banlist.objects.filter(user_id=request.user.id)[0].banlist
    except:
        ban_list = []

    ban_list += Banlist.objects.filter(banlist__contains=request.user.id).values_list('user_id', flat=True)
    loop_list = Loopship.objects.filter(user_id=request.user.id).values_list('friend_id', flat=True)

    tag_score = {}
    for post in Post_Tag.objects.filter(tag_id__in=tags):
        try:
            tag_score[post.post_id] += tags[str(post.tag_id)]['count']
        except KeyError:
            tag_score[post.post_id] = tags[str(post.tag_id)]['count']

    now = datetime.datetime.now()

    post_list = []
    for post in Post.objects.filter(date__range=[now-datetime.timedelta(days=7), now]).exclude(user_id__in=ban_list).exclude(user_id__in=loop_list):
        try:
            post_list.append([post, tag_score[post.id]])
        except KeyError:
            pass

    post_list.sort(key=lambda x: (-x[1]))
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
        ban_list = Banlist.objects.filter(user_id=request.user.id)[0].banlist
    except:
        ban_list = []

    ban_list += Banlist.objects.filter(banlist__contains=request.user.id).values_list('user_id', flat=True)

    if request.GET['last'] == '0':
        post_obj = Post.objects.select_related('project').select_related('user').all().exclude(user_id__in=ban_list).order_by('-id')[:5]
    else:
        post_obj = Post.objects.select_related('project').select_related('user').filter(id__lt=request.GET['last']).exclude(user_id__in=ban_list).order_by('-id')[:5]

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
    
    profile = Profile.objects.filter(user_id=request.user.id)[0]
    if request.GET['last'] == '0':
        if profile.group == 10:
            news_obj = NewsSerializer(News.objects.all(), many=True).data
        else:
            news_obj = NewsSerializer(News.objects.filter(group_id=profile.group), many=True).data         

        return Response({'posting':post_obj, 'news':news_obj}, status=status.HTTP_200_OK)

    else: return Response({'posting':post_obj})

@api_view(['GET', ])
@permission_classes((IsAuthenticated,))
def loop_load(request):
    loop = list(Loopship.objects.filter(user_id=request.user.id))

    loop_list = []
    for l in loop:
        loop_list.append(l.friend_id)

    now = datetime.datetime.now()

    if request.GET['last'] == '0':
        post_obj = Post.objects.select_related('project').select_related('user').filter(date__range=[now-datetime.timedelta(days=7), now], user_id__in=loop_list).order_by('-id')[:5]
    else:
        post_obj = Post.objects.select_related('project').select_related('user').filter(date__range=[now-datetime.timedelta(days=7), now], id__lt=request.GET['last'], user_id__in=loop_list).order_by('-id')[:5]

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

    if request.GET['last'] == '0':
        try:
            news_obj = NewsSerializer(News.objects.filter(group_id=request.GET['group_id']), many=True).data
        except:
            news_obj = NewsSerializer(News.objects.all(), many=True).data

        return Response({'posting':post_obj, 'news':news_obj}, status=status.HTTP_200_OK)
        
    else: return Response({'posting':post_obj})

@api_view(['GET', ])
@permission_classes((IsAuthenticated,))
def like_list_load(request):
    idx = request.GET['id']
    if request.GET['type'] == 'post':
        like_list = Like.objects.filter(post_id=idx).values_list('user_id', flat=True)
    
    elif request.GET['type'] == 'comment':
        like_list = CommentLike.objects.filter(comment_id=idx).values_list('user_id', flat=True)
    
    elif request.GET['type'] == 'cocomment':
        like_list = CocommentLike.objects.filter(cocomment_id=idx).values_list('user_id', flat=True)

    return Response(SimpleProfileSerializer(Profile.objects.filter(user_id__in=like_list), many=True).data, status=status.HTTP_200_OK)

@api_view(['POST'])
@permission_classes((IsAuthenticated,))
def report_posting(request):
    Report.objects.create(user_id=request.user.id, type=1, target_id=request.data['id'], reason=request.data['reason'])
    count = Report.objects.filter(type=1, target_id=request.data['id']).count()
    if count >= 3:
        report_alarm(count, 1, request.data['id'], request.data['reason'])
    return Response(status=status.HTTP_200_OK)
