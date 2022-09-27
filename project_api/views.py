from search.models import Get_log

from .serializers import ProjectPostSerializer, ProjectUserSerializer
from .models import Project, ProjectUser
from user_api.models import Profile
# from fcm.models import FcmToken
from fcm.push_fcm import tag_fcm
from post_api.models import PostImage, Like, BookMark, Post

from rest_framework import status
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated

# Create your views here.
@api_view(['POST', 'PUT', 'GET', 'DELETE'])
@permission_classes((IsAuthenticated,))
def project(request):
    user_id = request.user.id
    if request.method == 'POST':
        
        project_obj = Project.objects.create(project_name=request.data['project_name'], is_public=request.data['is_public'])
        project_obj = ProjectUser.objects.create(user_id=user_id, project_id=project_obj.id)
        
        return Response(ProjectUserSerializer(project_obj).data, status=status.HTTP_201_CREATED)

    elif request.method == 'PUT':
        type = request.GET['type']
        project_obj = Project.objects.filter(id=request.GET['id'])[0]
        if type == 'project_name':
            project_obj.project_name = request.data['project_name']
            project_obj.save()
            
        elif type == 'looper':
            profile_obj = Profile.objects.filter(user_id=user_id)[0]
            looper_list = request.data.getlist('looper')

            for looper in looper_list:
                ProjectUser.objects.create(project_id=project_obj.id, looper_id=looper, is_manager=False)
                tag_fcm(looper, profile_obj.real_name, user_id, project_obj.project_name, project_obj.id)
                    
        return Response(status=status.HTTP_200_OK)

    elif request.method == 'GET':
        try:
            project_obj = Project.objects.filter(id=request.GET['id'])[0]
        except IndexError:
            return Response(status=status.HTTP_404_NOT_FOUND)
        
        project = ProjectPostSerializer(project_obj).data            
        post_list = list(map(lambda x:x['id'], project['post']))
        like_list = dict(Like.objects.filter(user_id=request.user.id, post_id__in=post_list).values_list('post_id', 'user_id'))
        book_list = dict(BookMark.objects.filter(user_id=request.user.id, post_id__in=post_list).values_list('user_id', 'post_id'))
        for post in project['post']:
            if post['user_id'] == user_id:
                post.update({'is_user':1})
            else:
                post.update({'is_user':0})
            if post['id'] in like_list:
                post.update({"is_liked":1})
            else:
                post.update({"is_liked":0})        
            if post['id'] in book_list:
                post.update({"is_marked":1})
            else:
                post.update({"is_marked":0})

        return Response(project, status=status.HTTP_200_OK)

    elif request.method == 'DELETE':
        project_obj = Project.objects.filter(id=request.GET['id'])[0]

        for post in Post.objects.filter(project_id=request.GET['id']):
            for image in PostImage.objects.filter(post_id=post.id):
                image.image.delete(save=False)
                
        project_obj.delete()
        return Response("is deleted", status=status.HTTP_200_OK)