from datetime import datetime, date, timedelta

from rest_framework import status
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated

from project_api.models import Project

from .models import PostingRanking

from user_api.models import Profile
from tag.models import Post_Tag, Tag
from post_api.models import Post
from post_api.serializers import MainloadSerializer
from tag.models import Group

@api_view(['GET'])   
@permission_classes((IsAuthenticated, ))
def set_monthly_tag_count(request):
    if request.user.id != 5:
        return Response(stauts=status.HTTP_403_FORBIDDEN)
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
    last = PostingRanking.objects.last()

    if request.user.id != 5:
        return Response(stauts=status.HTTP_403_FORBIDDEN)
    group_list = Group.objects.all().values_list('id', flat=True)
    group_list = {i:[] for i in group_list}
    
    now = datetime.now()
    post_obj = Post.objects.filter(date__range=[now-timedelta(days=7), now]).prefetch_related('post_tag').order_by('-like_count', '-id')
    for post in post_obj:
        for tag in post.post_tag.filter(post_id=post.id).select_related('tag'):
            group_list[tag.tag.group_id].append(PostingRanking(post_id=post.id, group=tag.tag.group_id, score=post.like_count))

    for group in group_list:
        PostingRanking.objects.bulk_create(group_list[group][:10])
    PostingRanking.objects.filter(id__lte=last.id).delete()

    return Response(status=status.HTTP_200_OK)

@api_view(['GET'])   
@permission_classes((IsAuthenticated, ))
def set_profile_group(request):
    if request.user.id != 5:
        return Response(stauts=status.HTTP_403_FORBIDDEN)
    profile_obj = Profile.objects.all()
    for profile in profile_obj:
        project_group = {}
        project_obj = Project.objects.filter(user_id=profile.user_id)
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
            continue
        else:
            profile.group = max(project_group, key=project_group.get)
            profile.save()

    return Response(status=status.HTTP_200_OK)

@api_view(['GET'])
@permission_classes((IsAuthenticated,))
def career_board_ranking(request):
    ranked_post_obj = PostingRanking.objects.filter(group=request.GET['id']).select_related('post')
    post_list = []
    for ranked_post in ranked_post_obj:
        post_list.append(ranked_post.post)
    
    return Response(MainloadSerializer(post_list, many=True).data, status=status.HTTP_200_OK)