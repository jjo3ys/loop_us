import datetime

from rest_framework import status
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated

from .models import PostingRanking

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

@api_view(['GET'])
@permission_classes((IsAuthenticated,))
def career_board_ranking(request):
    ranked_post_obj = PostingRanking.objects.filter(group=request.GET['id']).select_related('post')
    post_list = []
    for ranked_post in ranked_post_obj:
        post_list.append(ranked_post.post)
    
    return Response(MainloadSerializer(post_list, many=True).data, status=status.HTTP_200_OK)
