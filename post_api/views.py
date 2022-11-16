from django.core.paginator import Paginator
from django.db.models import F, Q
from crawling_api.models import News, Youtube, Brunch
from project_api.models import Project, ProjectUser
# from search.models import Get_log, InterestTag
# from search.views import interest_tag

from tag.models import Post_Tag, Tag
# from fcm.models import FcmToken
from fcm.push_fcm import cocomment_fcm, cocomment_like_fcm, comment_fcm, department_fcm, like_fcm, report_alarm, comment_like_fcm, school_fcm, public_pj_fcm
from user_api.models import Banlist, InterestCompany, Profile, Report
from user_api.serializers import SimpleProfileSerializer

from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework import status

from .serializers import BrSerializer, CocommentSerializer, CommentSerializer, NewsSerializer,  PostingSerializer, MainloadSerializer, SimpleProjectserializer
from .models import CocommentLike, CommentLike, CorpLike, Post, PostImage, Like, BookMark, Cocomment, Comment, PostLink

from user_api.models import Company_Inform, Alarm
from loop.models import Loopship
#from sentence_transformers import SentenceTransformer, util
import datetime
import random
# Create your views here.
#emb = SentenceTransformer("jhgan/ko-sroberta-multitask")
@api_view(['POST', 'PUT', 'GET', 'DELETE'])
@permission_classes((IsAuthenticated,))
def posting(request):
    user_id = request.user.id
    if request.method == 'POST': 
        tags = request.data.getlist('tag')
        '''
        q = Post.objects.filter(project_id=request.GET['id'])
        if q.count() == 0:
            q = Post.objects.filter(user_id=user_id)
            if q.count() == 0:
                user_profile = Profile.object.filter(user_id=user_id)[0]
                
             
        
        compare = q.last().contents
        compare = emb.encode(comapare, convert_to_tensor=True)
        query = emb.encode(request.data['contents'], convert_to_tensor=True)   
        scores = util.pytorch_cos_sim(query, compare).reshape(2)
        '''
        post_obj = Post.objects.create(user_id=user_id, 
                                        project_id=request.GET['id'],    
                                        contents=request.data['contents'])
        project_obj = Project.objects.get(id=request.GET['id'])

        for id, image in enumerate(request.FILES.getlist('image')):
            image_obj = PostImage.objects.create(post_id=post_obj.id, image=image)
            if id == 0 and not project_obj.tag_company:
                project_obj.thumbnail=image_obj.id
        
        # interest_list = InterestTag.objects.get_or_create(user_id=user_id)[0]

        for link in request.data.getlist('link'):
            PostLink.objects.create(post_id=post_obj.id, link=link)

        for tag in tags:
            tag_obj, created = Tag.objects.get_or_create(tag=tag)
            Post_Tag.objects.create(post=post_obj, tag=tag_obj)
            # interest_tag(interest_list, 'plus', tag_obj.id, 10)
            if not created:
                tag_obj.count += 1
                tag_obj.save()

        # interest_list.save()
        
        project_obj.post_update_date = datetime.datetime.now()
        project_obj.save()

        ProjectUser.objects.filter(user_id=user_id, project_id=request.GET['id']).update(post_count=F('post_count') + 1)
        
        # if request.user.is_staff:
        #     official_obj = Profile.objects.filter(user_id=user_id)[0]
        #     if official_obj.type == 1:
        #         department_fcm(official_obj.department_id, post_obj.id, user_id)
        #     elif official_obj.type == 3:
        #         school_fcm(official_obj.school_id, post_obj.id, user_id)
                
        if project_obj.is_public:
            public_pj_fcm(project_obj.id, post_obj.id, user_id, project_obj.project_name)
        return Response(PostingSerializer(post_obj).data, status=status.HTTP_200_OK)
    
    elif request.method == 'PUT':
        post_obj = Post.objects.filter(id=request.GET['id']).select_related('project')[0]
        post_obj.contents = request.data['contents']
        origin_tag_obj = Post_Tag.objects.filter(post_id=post_obj.id).select_related('tag')
        origin_tag_list = origin_tag_obj.values_list('tag__tag', flat=True)
        tag_list = request.data.getlist('tag')

        # interest_list = InterestTag.objects.get_or_create(user_id=user_id)[0]
        for tag in tag_list:
            if tag not in origin_tag_list:
                tag_obj, created = Tag.objects.get_or_create(tag=tag)
                Post_Tag.objects.create(tag=tag_obj, post_id=post_obj.id)
                # interest_list = interest_tag(interest_list, 'plus', tag_obj.id, 10)
                
                if not created:
                    tag_obj.count += 1
                    tag_obj.save()

        for tag in origin_tag_obj:
            if tag.tag.tag not in tag_list:
                # interest_list = interest_tag(interest_list, 'minus', tag.tag_id, 10)
                tag.tag.count -=1

                tag.delete()
                if tag.tag.count == 0:
                    tag.tag.delete()
                else:
                    tag.tag.save()
        
        # interest_list.save()
        post_obj.save()
        return Response(status=status.HTTP_200_OK)
    
    elif request.method == 'GET':
        try:
            post_obj = Post.objects.filter(id=request.GET['id']).select_related('project')[0]
        except IndexError:
            return Response(status=status.HTTP_404_NOT_FOUND)
        post_obj.view_count += 1
        post_obj.save()
        post_obj = PostingSerializer(post_obj).data

        if user_id == post_obj['user_id']:
            post_obj.update({"is_user":1})
        else:
            # Get_log.objects.create(user_id=user_id, target_id=request.GET['id'], type=4)
            post_obj.update({"is_user":0})

        exists = Like.objects.filter(user_id=user_id, post_id=request.GET['id']).exists()
        if exists:
            post_obj.update({"is_liked":1})
        else:
            post_obj.update({"is_liked":0})
        
        commentlike = dict(CommentLike.objects.select_related('comment').filter(user_id=user_id, comment__post_id=request.GET['id']).values_list('comment_id', 'user_id'))
        cocomment_like = dict(CocommentLike.objects.select_related('cocomment__comment').filter(user_id=user_id, cocomment__comment__post_id=request.GET['id']).values_list('cocomment_id', 'user_id'))
        for comment in post_obj['comments']:
            if comment['id'] in commentlike:
                comment.update({'is_liked':1})
            else:
                comment.update({'is_liked':0})
    
            for cocomment in comment['cocomments']['cocomment']:                
                if cocomment['id'] in cocomment_like:
                    cocomment.update({'is_liked':1})
                else:
                    cocomment.update({'is_liked':0})

        exists = BookMark.objects.filter(user_id=user_id, post_id=request.GET['id']).exists()
        if exists:
            post_obj.update({"is_marked":1})
        else:
            post_obj.update({"is_marked":0})

        return Response(post_obj, status=status.HTTP_200_OK)
    
    elif request.method == 'DELETE':
        post_obj = Post.objects.get(id=request.GET['id'])
        contents_image_obj = PostImage.objects.filter(post_id=post_obj.id)
        # interest_list = InterestTag.objects.get_or_create(user_id=user_id)[0]
        tag_obj = Post_Tag.objects.filter(post_id=post_obj.id).select_related('tag')

        for tag in tag_obj:
            # interest_list = interest_tag(interest_list, 'minus', tag.tag_id, 10)
            tag.tag.count = tag.tag.count-1
                
            tag.delete()
            if tag.tag.count == 0:
                tag.tag.delete()
            else: 
                tag.tag.save()
        
        if post_obj.project.tag_company: pass
        else:
            thumbnail_id = post_obj.project.thumbnail
            if contents_image_obj.count() != 0:
                for image in contents_image_obj:
                    image.image.delete(save=False)
                    if image.id == thumbnail_id:
                        post = Post.objects.filter(project_id=post_obj.project_id).exclude(id=post_obj.id)
                        post_list = list(post.values_list('id', flat=True))
                        img_obj = PostImage.objects.filter(post_id__in=post_list)
                        if post.count() == 0 or img_obj.count() == 0:
                            post_obj.project.thumbnail = 0
                        else:
                            post_obj.project.thumbnail = PostImage.objects.filter(post_id=img_obj.last().post_id).first().id
                        if post.last():
                            post_obj.project.post_update_date = post.last().date
                        else:
                            post_obj.project.post_update_date = None
                        post_obj.project.save()

        ProjectUser.objects.filter(user_id=user_id, project_id=post_obj.project_id).update(post_count=F('post_count')-1)
        Alarm.objects.filter(type__in=[4, 5, 6, 7, 8, 9], target_id=request.GET['id']).delete()
        post_obj.delete()
        return Response("delete posting", status=status.HTTP_200_OK)

@api_view(['POST', 'DELETE', 'PUT', 'GET'])
@permission_classes((IsAuthenticated,))
def comment(request):   
    user_id = request.user.id
    if request.method =='POST':
        if request.GET['type'] == 'comment':
            comment_obj = Comment.objects.create(user_id=user_id,
                                                 post_id=request.GET['id'],#포스트 id
                                                 content=request.data['content'])
            try:
                post_obj = Post.objects.filter(id=request.GET['id'])[0]
            except: return Response(status=status.HTTP_404_NOT_FOUND)
            if user_id != post_obj.user_id:
                profile_obj = Profile.objects.filter(user_id=user_id)
                try:
                    if profile_obj:
                        real_name = profile_obj[0].real_name
                    else:
                        real_name = Company_Inform.objects.filter(user_id=user_id)[0].company_name
                except: return Response(status=status.HTTP_404_NOT_FOUND)
                comment_fcm(post_obj.user_id, real_name, post_obj.id, user_id)
                is_student = int(request.GET['is_student'])
                if is_student and Company_Inform.objects.filter(user_id=post_obj.user_id).exists():
                    obj, created = InterestCompany.objects.get_or_create(company=post_obj.user_id, user_id=user_id)
                    if not created:
                        obj.delete()
                        InterestCompany.objects.create(company=post_obj.user_id, user_id=user_id)

            return Response(CommentSerializer(comment_obj).data,status=status.HTTP_201_CREATED)

        elif request.GET['type'] == 'cocomment':
            cocomment_obj = Cocomment.objects.create(user_id=user_id,
                                                     comment_id=request.GET['id'],#댓글 id
                                                     content=request.data['content'],
                                                     tagged_id=request.data['tagged_user'])
            if int(user_id) != int(request.data['tagged_user']) or int(user_id) != int(cocomment_obj.comment.user_id):
                
                profile_obj = Profile.objects.filter(user_id=user_id)
                try:
                    if profile_obj:
                        real_name = profile_obj[0].real_name
                    else:
                        real_name = Company_Inform.objects.filter(user_id=user_id)[0].company_name
                except: return Response(status=status.HTTP_404_NOT_FOUND)
                cocomment_fcm(request.data['tagged_user'], real_name, cocomment_obj.id, user_id, cocomment_obj.comment.post_id)

            return Response(CocommentSerializer(cocomment_obj).data, status=status.HTTP_201_CREATED)
    
    elif request.method =='PUT':
        if request.GET['type'] == 'comment':
            comment_obj = Comment.objects.filter(id=request.data['id'])[0]#댓글 id
            comment_obj.content=request.data['content']
            comment_obj.save()

            return Response(CommentSerializer(comment_obj).data,status=status.HTTP_201_CREATED)

        elif request.GET['type'] == 'cocomment':
            cocomment_obj = Cocomment.objects.filter(id=request.data['id'])[0]#대댓글 id
            cocomment_obj.content=request.data['content']
            cocomment_obj.save()
            
            return Response(CocommentSerializer(cocomment_obj).data, status=status.HTTP_201_CREATED)
    
    elif request.method == 'DELETE':
        if request.GET['type'] == 'comment':
            try:
                comment = Comment.objects.filter(id=request.GET['id'])[0]#댓글 id
                Alarm.objects.filter(type__in=[5, 7], target_id=comment.post_id)
                comment.delete()
            except:
                return Response(status=status.HTTP_404_NOT_FOUND)

        elif request.GET['type'] == 'cocomment':
            try:
                cocomment = Cocomment.objects.filter(id=request.GET['id'])[0]#대댓글 id
                Alarm.objects.filter(type__in=[6, 8], target_id=cocomment.comment.post_id)
                cocomment.delete()
            except:
                return Response(status=status.HTTP_404_NOT_FOUND)
        
        return Response(status=status.HTTP_200_OK)

    elif request.method == 'GET':
        if request.GET['type'] == 'comment':
            comment_obj = Comment.objects.filter(post_id=request.GET['id'], id__lt = request.GET['last']).order_by('-id')
            return Response(CommentSerializer(comment_obj[:10], many=True).data, status=status.HTTP_200_OK)
            
        elif request.GET['type'] == 'cocomment':
            cocomment_obj = Cocomment.objects.filter(comment_id=request.GET['id'], id__gt = request.GET['last'])
            return Response(CocommentSerializer(cocomment_obj[:10], many=True).data, status=status.HTTP_200_OK)

@api_view(['POST', ])
@permission_classes((IsAuthenticated,))
def like(request):
    user_id = request.user.id
    type = request.GET['type']
    idx = request.GET['id']
    if type =='post':
        is_student = int(request.GET['is_student'])
        if is_student:
            try:
                like_obj, created = Like.objects.get_or_create(post_id=idx, user_id=user_id)
            except: return Response(status=status.HTTP_404_NOT_FOUND)
        else:
            try:
                like_obj, created = CorpLike.objects.get_or_create(post_id=idx, user_id=user_id)
            except:  return Response(status=status.HTTP_404_NOT_FOUND)

        if not created:
            like_obj.post.like_count -= 1
            like_obj.post.save()
            like_obj.delete()
            return Response('unliked posting', status=status.HTTP_202_ACCEPTED)

        else:
            like_obj.post.like_count += 1
            like_obj.post.save()
            if like_obj.post.user_id != user_id:
                try:
                    real_name = Profile.objects.filter(user_id=user_id)[0].real_name
                    like_fcm(like_obj.post.user_id, real_name, idx, user_id)
                except: pass
                if is_student and Company_Inform.objects.filter(user_id=like_obj.post.user_id).exists():
                    obj, created = InterestCompany.objects.get_or_create(company=like_obj.post.user_id, user_id=user_id)  
                    if not created:
                        obj.delete()
                        InterestCompany.objects.create(company=like_obj.post.user_id, user_id=user_id)

            return Response('liked posting', status=status.HTTP_202_ACCEPTED)
                
    elif type =='comment':
        try:
            like_obj, created = CommentLike.objects.get_or_create(comment_id=idx, user_id=user_id)
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
            if like_obj.comment.user_id != user_id:
                try:
                    # token = FcmToken.objects.filter(user_id=like_obj.post.user_id)[0]
                    real_name = Profile.objects.filter(user_id=user_id)[0].real_name
                    comment_like_fcm(like_obj.comment.user_id, real_name, idx, user_id, like_obj.comment.post_id)
                except:
                    pass

            return Response('liked comment', status=status.HTTP_202_ACCEPTED)  
                 
    elif type =='cocomment':
        try:
            like_obj, created = CocommentLike.objects.get_or_create(cocomment_id=idx, user_id=user_id)
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
            if like_obj.cocomment.user_id != user_id:
                try:
                    # token = FcmToken.objects.filter(user_id=like_obj.post.user_id)[0]
                    real_name = Profile.objects.filter(user_id=user_id)[0].real_name
                    cocomment_like_fcm(like_obj.cocomment.user_id, real_name, idx, user_id, like_obj.cocomment.comment.post_id)
                except:
                    pass

            return Response('liked cocomment', status=status.HTTP_202_ACCEPTED)    

@api_view(['GET', ])
@permission_classes((IsAuthenticated,))
def like_list_load(request):
    idx = request.GET['id']
    if request.GET['type'] == 'post':
        corp_list = CorpLike.objects.filter(post_id=idx).values_list('user_id', flat=True)
        like_list = Like.objects.filter(post_id=idx).values_list('user_id', flat=True)
        like_list = like_list.union(corp_list)
    
    elif request.GET['type'] == 'comment':
        like_list = CommentLike.objects.filter(comment_id=idx).values_list('user_id', flat=True)
    
    elif request.GET['type'] == 'cocomment':
        like_list = CocommentLike.objects.filter(cocomment_id=idx).values_list('user_id', flat=True)

    return Response(SimpleProfileSerializer(Profile.objects.filter(user_id__in=like_list).select_related('school', 'department'), many=True).data, status=status.HTTP_200_OK)
                    
@api_view(['POST', ])
@permission_classes((IsAuthenticated,))
def bookmark(request):
    user_id = request.user.id
    idx = request.GET['id']
    try:
        book_obj, created = BookMark.objects.get_or_create(post_id=idx, user_id=user_id)
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
    user_id = request.user.id
    bookmark_list = BookMark.objects.filter(user_id=user_id).select_related('post__project').order_by('-id')
    bookmark_list = Paginator(bookmark_list, 10)
    if bookmark_list.num_pages < int(request.GET['page']):
        return Response(status=status.HTTP_204_NO_CONTENT)

    bookmark_list = bookmark_list.get_page(request.GET['page'])
    post_obj = []
    for bookmark in bookmark_list:
        post_obj.append(bookmark.post)

    like_list = dict(Like.objects.filter(user_id=user_id, post__in=post_obj).values_list('post_id', 'user_id'))
    post_obj = MainloadSerializer(post_obj, many=True).data
    for p in post_obj:
        if p['id'] in like_list:
            p.update({"is_liked":1})
        else:
            p.update({"is_liked":0})
        
        p.update({"is_marked":1,
                  "is_user":1})

    return Response(post_obj, status=status.HTTP_200_OK)

# @api_view(['GET', ])
# @permission_classes((IsAuthenticated,))
# def recommend_load(request):
#     user_id = request.user.id
#     tags = InterestTag.objects.filter(user_id=user_id)[0].tag_list
#     try:
#         ban_list = Banlist.objects.filter(user_id=user_id)[0].banlist
#     except:
#         ban_list = []

#     ban_list += Banlist.objects.filter(banlist__contains=user_id).values_list('user_id', flat=True)
#     loop_list = Loopship.objects.filter(user_id=user_id).values_list('friend_id', flat=True)

#     tag_score = {}
#     for post in Post_Tag.objects.filter(tag_id__in=tags):
#         try:
#             tag_score[post.post_id] += tags[str(post.tag_id)]['count']
#         except KeyError:
#             tag_score[post.post_id] = tags[str(post.tag_id)]['count']

#     now = datetime.datetime.now()

#     post_list = []
#     for post in Post.objects.filter(date__range=[now-datetime.timedelta(days=7), now]).exclude(user_id__in=ban_list).exclude(user_id__in=loop_list):
#         try:
#             post_list.append([post, tag_score[post.id]])
#         except KeyError:
#             pass

#     post_list.sort(key=lambda x: (-x[1]))
#     page = int(request.GET['page'])
#     post_obj = MainloadSerializer([x[0] for x in post_list[5*(page-1):5*page]], many=True).data
#     post_list = 0

#     for p in post_obj:
#         if p['user_id'] == user_id:
#             p.update({"is_user":1})
#         else:
#             p.update({"is_user":0})

        
#         if Like.objects.filter(user_id=user_id, post_id=p['id']).exists():
#             p.update({"is_liked":1})
#         else:
#             p.update({"is_liked":0})

        
#         if BookMark.objects.filter(user_id=user_id, post_id=p['id']).exists():
#             p.update({"is_marked":1})
#         else:
#             p.update({"is_marked":0})

#     return Response(post_obj, status=status.HTTP_200_OK)
    
@api_view(['GET', ])
@permission_classes((IsAuthenticated,))
def main_load(request):
    user_id = request.user.id
    try:
        ban_list = Banlist.objects.filter(user_id=user_id)[0].banlist
    except:
        ban_list = []

    ban_list += Banlist.objects.filter(banlist__contains=user_id).values_list('user_id', flat=True)
    profile = Profile.objects.filter(user_id=user_id)
    if profile.exists():
        ban_list += Profile.objects.filter(Q(type=1)& ~Q(department_id=profile[0].department_id)).values_list('user_id', flat=True)
        
    else:
        ban_list += Profile.objects.filter(type=1).values_list('user_id', flat=True)
        
    if request.GET['last'] == '0':
        post_obj = Post.objects.all().select_related('user', 'project').exclude(user_id__in=ban_list).order_by('-id')[:20]
    else:
        post_obj = Post.objects.filter(id__lt=request.GET['last']).select_related('user', 'project').exclude(user_id__in=ban_list).order_by('-id')[:20]

    post_list = list(post_obj.values_list('id', flat=True))
    like_list = dict(Like.objects.filter(user_id=user_id, post_id__in=post_list).values_list('post_id', 'user_id'))
    book_list = dict(BookMark.objects.filter(user_id=user_id, post_id__in=post_list).values_list('post_id', 'user_id'))
    post_obj = MainloadSerializer(post_obj, many=True).data

    for p in post_obj:
        if p['user_id'] == user_id:
            p.update({"is_user":1})
        else:
            p.update({"is_user":0})
        
        if p['id'] in like_list:
            p.update({'is_liked':1})
        else:
            p.update({'is_liked':0})

        if p['id'] in book_list:
            p.update({'is_marked':1})
        else:
            p.update({'is_marked':0})
    
    if request.GET['last'] == '0':
        
        project_obj = ProjectUser.objects.filter(user_id=user_id).select_related('project').order_by('post_count').first()
        if project_obj:
            project_obj = SimpleProjectserializer(project_obj.project).data
            
        # if profile.group == 16:
        #     news_obj = News.objects.all().order_by('?')
        #     br_obj = Brunch.objects.all().order_by('?')
        #     yt_obj = list(Youtube.objects.all().order_by('?').values_list('urls', flat=True))
        # else:
        # news_obj = News.objects.filter(group_id=profile.group).order_by('?')
        # br_obj = Brunch.objects.filter(group_id=profile.group).order_by('?')
        # yt_obj = list(Youtube.objects.filter(group_id=profile.group).order_by('?').values_list('urls', flat=True))
        news_obj = News.objects.all().order_by('?')
        br_obj = Brunch.objects.all().order_by('?')
        yt_obj = list(Youtube.objects.all().order_by('?').values_list('urls', flat=True))
            
        return Response({'posting':post_obj, 
                         'brunch':BrSerializer(br_obj, many=True).data, 
                         'news': NewsSerializer(news_obj, many=True).data,
                         'youtube':yt_obj, 
                         'project':project_obj}, status=status.HTTP_200_OK)
    else: return Response({'posting':post_obj})

@api_view(['GET', ])
@permission_classes((IsAuthenticated,))
def loop_load(request):
    user_id = request.user.id
    loop_list = list(Loopship.objects.filter(user_id=user_id).values_list('friend_id', flat=True))
    loop_list.append(user_id)

    ban_list = Banlist.objects.filter(banlist__contains=user_id).values_list('user_id', flat=True)
    if request.GET['last'] == '0':
        post_obj = Post.objects.filter(user_id__in=loop_list).exclude(user_id__in=ban_list).select_related('project').order_by('-id')[:20]
    else:
        post_obj = Post.objects.filter(id__lt=request.GET['last'], user_id__in=loop_list).exclude(user_id__in=ban_list).select_related('project').order_by('-id')[:20]

    post_list = list(post_obj.values_list('id', flat=True))
    like_list = dict(Like.objects.filter(user_id=user_id, post_id__in=post_list).values_list('post_id', 'user_id'))
    book_list = dict(BookMark.objects.filter(user_id=user_id, post_id__in=post_list).values_list('post_id', 'user_id'))
    post_obj = MainloadSerializer(post_obj, many=True).data

    for p in post_obj:
        if p['user_id'] == user_id:
            p.update({"is_user":1})
        else:
            p.update({"is_user":0})
        
        if p['id'] in like_list:
            p.update({'is_liked':1})
        else:
            p.update({'is_liked':0})

        if p['id'] in book_list:
            p.update({'is_marked':1})
        else:
            p.update({'is_marked':0})    
    
    if request.GET['last'] == '0':
        profile = Profile.objects.filter(user_id=user_id)
        if profile.exists():
            profile = profile[0]
        else:
            profile = Company_Inform.objects.filter(user_id=user_id)[0]
            
        project_obj = ProjectUser.objects.filter(user_id=user_id).select_related('project').order_by('post_count').first()
        if project_obj:
            project_obj = SimpleProjectserializer(project_obj.project).data
            
        if profile.group == 16:
            news_obj = News.objects.all().order_by('?')
            br_obj = Brunch.objects.all().order_by('?')
            yt_obj = list(Youtube.objects.all().order_by('?').values_list('urls', flat=True))
        else:
            news_obj = News.objects.filter(group_id=profile.group).order_by('?')
            br_obj = Brunch.objects.filter(group_id=profile.group).order_by('?')
            yt_obj = list(Youtube.objects.all().order_by('?').values_list('urls', flat=True))
            
        return Response({'posting':post_obj, 
                         'brunch':BrSerializer(br_obj, many=True).data, 
                         'news': NewsSerializer(news_obj, many=True).data,
                         'youtube':yt_obj, 
                         'project':project_obj}, status=status.HTTP_200_OK)
    else: return Response({'posting':post_obj})
    
@api_view(['POST'])
@permission_classes((IsAuthenticated,))
def report(request):
    user_id = request.user.id
    if request.GET['type'] == 'post':
        Report.objects.create(user_id=user_id, type=1, target_id=request.data['id'], reason=request.data['reason'])
        count = Report.objects.filter(type=1, target_id=request.data['id']).count()
        if count >= 3:
            report_alarm(count, 1, request.data['id'], request.data['reason'])

    elif request.GET['type'] == 'comment':
        Report.objects.create(user_id=user_id, type=2, target_id=request.data['id'], reason=request.data['reason'])
        count = Report.objects.filter(type=2, target_id=request.data['id']).count()
        if count >= 3:
            report_alarm(count, 2, request.data['id'], request.data['reason'])

    elif request.GET['type'] == 'cocomment':
        Report.objects.create(user_id=user_id, type=3, target_id=request.data['id'], reason=request.data['reason'])
        count = Report.objects.filter(type=3, target_id=request.data['id']).count()
        if count >= 3:
            report_alarm(count, 3, request.data['id'], request.data['reason'])
            
    return Response(status=status.HTTP_200_OK)
