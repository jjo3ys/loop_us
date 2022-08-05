from datetime import datetime, date, timedelta

from django.core.paginator import Paginator

from rest_framework import status
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated

from project_api.models import Project
from user_api.serializers import RankProfileSerailizer, SchoolRankProfileSerailizer

from .models import PostingRanking

from user_api.models import Profile, School
from tag.models import Post_Tag, Tag
from tag.serializer import TagSerializer
from post_api.models import Post
from post_api.serializers import MainloadSerializer
from tag.models import Group

@api_view(['POST', 'GET'])   
@permission_classes((IsAuthenticated, ))
def posting_with_group(request):
    if request.method == 'POST' and request.user.id == 5:
        today = date.today()
        group_obj= Group.objects.all()
        group_list = group_obj.values_list('id', flat=True)
        group_list = {i:{} for i in group_list}

        post_obj = Post.objects.filter(date__range=[today-timedelta(days=183), today]).prefetch_related('post_tag')

        for post in post_obj:
            month = str(post.date.month)
            for tag in post.post_tag.filter(post_id=post.id).select_related('tag'):
                if month not in group_list[tag.tag.group_id]:
                    group_list[tag.tag.group_id][month] = 1
                else:
                    group_list[tag.tag.group_id][month] += 1
        
        for group in group_list:
            g_obj = group_obj.filter(id=group)[0]
            g_obj.monthly_count = group_list[group]
            g_obj.save()
        return Response(status=status.HTTP_200_OK)

    elif request.method == 'GET':
        lastmonth = date.today().month
        group_obj = Group.objects.filter(id=request.GET['id'])[0]
        for i in range(1, 7):
            if lastmonth - i <= 0:
                month = str(12 + lastmonth - i)
            else:
                month = str(lastmonth - i)
            if month not in group_obj.monthly_count:
                group_obj.monthly_count[month] = 0
        
        return Response({'monthly_count':group_obj.monthly_count}, status=status.HTTP_200_OK)
    else:
        return Response(status=status.HTTP_403_FORBIDDEN)

@api_view(['GET'])   
@permission_classes((IsAuthenticated, ))
def monthly_tag_count(request):
    if request.user.id != 5:
        return Response(status=status.HTTP_403_FORBIDDEN)
    today = date.today()
    post_tags = Post_Tag.objects.select_related('post').filter(post__date__range=[today-timedelta(days=183), today])
    for tag in post_tags:
        month = str(tag.post.date.month)
        if month not in tag.tag.monthly_count:
            tag.tag.monthly_count[month] = 1
        else:
            tag.tag.monthly_count[month] += 1
        tag.tag.save()

    return Response(status=status.HTTP_200_OK)

@api_view(['GET'])   
@permission_classes((IsAuthenticated, ))
def posting_ranking(request):
    if request.user.id != 5:
        return Response(status=status.HTTP_403_FORBIDDEN)
    group_list = Group.objects.all().values_list('id', flat=True)
    group_list = {i:[] for i in group_list}
    posting_list = []
    now = datetime.now()
    post_obj = Post.objects.filter(date__range=[now-timedelta(days=7), now]).prefetch_related('post_tag').order_by('-like_count', '-id')
    for post in post_obj:
        for tag in post.post_tag.filter(post_id=post.id).select_related('tag'):
            if  post.id not in group_list[tag.tag.group_id] and len(group_list[tag.tag.group_id]) < 10:
                group_list[tag.tag.group_id].append(post.id)
                posting_list.append(PostingRanking(post_id=post.id, group=tag.tag.group_id, score=post.like_count))
    
    last = PostingRanking.objects.last()
    PostingRanking.objects.bulk_create(posting_list)
    try:
        PostingRanking.objects.filter(id__lte=last.id).delete()
    except AttributeError:
        pass
    return Response(status=status.HTTP_200_OK)

@api_view(['GET'])   
@permission_classes((IsAuthenticated, ))
def project_group(request):
    if request.user.id != 5:
        return Response(status=status.HTTP_403_FORBIDDEN)
    now = datetime.now()
    project_obj = Project.objects.filter(post_update_date__range=[now-timedelta(days=1), now]).prefetch_related('post')
    for project in project_obj:
        group = {}
        post_list =  project.post.filter(project_id=project.id).values_list('id', flat=True)
        group_list = Post_Tag.objects.filter(post_id__in=post_list).select_related('tag').values_list('tag__group_id', flat=True)
        for id in group_list:
            if id in group:
                group[id] += 1
            else:
                group[id] = 1
        if len(group) == 0:
            continue        
        project.group = max(group.items(), key=lambda x: x[1])[0]
        project.save()
    return Response(status=status.HTTP_200_OK)

@api_view(['GET'])   
@permission_classes((IsAuthenticated, ))
def profile_group(request):
    if request.user.id != 5:
        return Response(status=status.HTTP_403_FORBIDDEN)
    profile_obj = Profile.objects.all()
    for profile in profile_obj:
        project_group = {}
        project_obj = Project.objects.filter(user_id=profile.user_id)
        for project in project_obj:
            group_id = project.group
            if group_id == 10:
                continue
            if group_id in project_group:
                project_group[group_id] += 1
            else:
                project_group[group_id] = 1     

        if len(project_group) == 0:
            continue

        if max(project_group, key=project_group.get) != profile.group:
            profile.last_rank=0
        profile.group = max(project_group, key=project_group.get)
        profile.save()

    return Response(status=status.HTTP_200_OK)

@api_view(['GET'])
@permission_classes((IsAuthenticated,))
def user_ranking(request):
    if request.user.id != 5:
        return Response(status=status.HTTP_403_FORBIDDEN)
    profile_obj = Profile.objects.all()
    group_list = Group.objects.all().values_list('id', flat=True)
    score_list = {}
    for g in group_list:
        score_list[g] = {}
    now = datetime.now()

    for profile in profile_obj:
        post_obj = Post.objects.filter(user_id=profile.user_id)
        recent_post_count = post_obj.filter(date__range = [now-timedelta(days=30), now]).count()
        score = sum(post_obj.values_list('like_count', flat=True)) + 0.5 * sum(post_obj.values_list('view_count', flat=True)) + 2 * recent_post_count
        score_list[profile.group][profile] = score
    
    for group in score_list:
        sorted_list = sorted(score_list[group].items(), key=lambda x:-x[1])
        for i, profile in enumerate(sorted_list):
            profile[0].score = profile[1]
            profile[0].last_rank = profile[0].rank
            profile[0].rank = i+1
            profile[0].save()
    
    school_obj = School.objects.all()
    for school in school_obj:
        profile_obj = Profile.objects.filter(school=school).order_by('-score')
        for group in group_list:
            group_school_profile_obj = profile_obj.filter(group=group)
            for i , profile in enumerate(group_school_profile_obj):
                profile.school_last_rank = profile.school_rank
                profile.school_rank = i+1
                profile.save()
    
    return Response(status=status.HTTP_200_OK)

@api_view(['GET'])
@permission_classes((IsAuthenticated,))
def career_board_ranking(request):
    group_id = request.GET['id']

    if request.GET['type'] == 'main':
        return_dict = {}
        ranked_post_obj = PostingRanking.objects.filter(group=group_id).select_related('post')
        post_list = []
        for ranked_post in ranked_post_obj:
            post_list.append(ranked_post.post)

        profile = Profile.objects.filter(user_id=request.user.id)[0]
        return_dict['posting'] = MainloadSerializer(post_list, many=True).data
        obj = Profile.objects.filter(group=group_id)
        
        return_dict['group_ranking'] = RankProfileSerailizer(obj.exclude(rank=0).order_by('rank')[:3], many=True).data
        return_dict['school_ranking'] = SchoolRankProfileSerailizer(obj.filter(school_id=profile.school_id).exclude(school_rank=0).order_by('school_rank')[:3], many=True).data
        return_dict['tag'] = TagSerializer(Tag.objects.filter(group_id=group_id).order_by('-count')[:5], many=True).data
        return Response(return_dict, status=status.HTTP_200_OK)
    
    elif request.GET['type'] == 'school':
        profile = Profile.objects.filter(user_id=request.user.id)[0]
        profile_obj = Profile.objects.filter(school_id=profile.school_id, group=group_id).exclude(rank=0).order_by('school_rank')[:100]
        return Response(SchoolRankProfileSerailizer(profile_obj, many=True).data, status=status.HTTP_200_OK)
    
    elif request.GET['type'] == 'group':
        profile_obj = Profile.objects.filter(group=group_id).exclude(rank=0).order_by('rank')[:100]
        return Response(RankProfileSerailizer(profile_obj, many=True).data, status=status.HTTP_200_OK)