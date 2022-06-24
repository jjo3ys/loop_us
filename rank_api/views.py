import datetime

from rest_framework import status
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated

from project_api.models import Project

from .models import PostingRanking

from user_api.models import Profile
from post_api.models import Post
from post_api.serializers import MainloadSerializer
from tag.models import Group

def posting_ranking():
    group_list = Group.objects.all().values_list('id', flat=True)
    group_list = {i:[] for i in group_list}
    
    now = datetime.datetime.now()
    post_obj = Post.objects.filter(date__range=[now-datetime.timedelta(days=7), now]).select_related('project').order_by('-like_count', '-id')
    
    for post in post_obj:
        group_list[post.project.group].append(PostingRanking(post_id=post.id, group=post.project.group, score=post.like_count))

    for group in group_list:
        PostingRanking.objects.bulk_create(group_list[group][:10])

def set_profile_group():
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

@api_view(['GET'])
@permission_classes((IsAuthenticated,))
def career_board_ranking(request):
    ranked_post_obj = PostingRanking.objects.filter(group=request.GET['id']).select_related('post')
    post_list = []
    for ranked_post in ranked_post_obj:
        post_list.append(ranked_post.post)
    
    return Response(MainloadSerializer(post_list, many=True).data, status=status.HTTP_200_OK)
