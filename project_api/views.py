from search.models import Get_log

from .serializers import ProjectPostSerializer
from .models import Project, TagLooper
from user_api.models import Profile
from fcm.models import FcmToken
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
    if request.method == 'POST':
        user = request.user

        start_date = request.data['start_date']
        end_date = request.data['end_date']

        if request.data['end_date'] == '':
            end_date = None

        profile_obj = Profile.objects.get(user_id=user.id)    
        project_obj = Project.objects.create(user=user, project_name = request.data['project_name'], 
                                            introduction = request.data['introduction'],
                                            start_date = start_date,
                                            end_date = end_date)

        return Response(ProjectPostSerializer(project_obj).data, status=status.HTTP_201_CREATED)

    elif request.method == 'PUT':
        type = request.GET['type']
        project_obj = Project.objects.get(id=request.GET['id'])
        if type == 'project_name':
            project_obj.project_name = request.data['project_name']

        elif type == 'date':
            start_date = request.data['start_date']
            end_date = request.data['end_date']
            if request.data['end_date'] == '':
                end_date = None

            project_obj.start_date = start_date
            project_obj.end_date = end_date
        
        elif type == 'introduction':
            project_obj.introduction = request.data['introduction']

        elif type == 'looper':
            profile_obj = Profile.objects.get(user_id=request.user.id)
            looper_list = eval(request.data['looper'])

            old_looper = TagLooper.objects.filter(project_id=project_obj.id)
            for looper in old_looper:
                if looper.looper.id not in looper_list:
                    looper.delete()

            for looper in looper_list:
                looper, created = TagLooper.objects.get_or_create(project_id=project_obj.id, looper_id=looper)
                if created:
                    try:
                        token = FcmToken.objects.get(user_id=looper.looper_id)
                        tag_fcm(token, profile_obj.real_name, request.user.id, project_obj.project_name, project_obj.id)
                    except:
                        pass
            
        project_obj.save()
        return Response(status=status.HTTP_200_OK)

    elif request.method == 'GET':
        try:
            project_obj = Project.objects.get(id=request.GET['id'])
        except Project.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)

        project = ProjectPostSerializer(project_obj).data
        if request.user.id == project_obj.user_id:
            project.update({"is_user":1})
        else:
            Get_log.objects.create(user_id=request.user.id, target_id=request.GET['id'], type=3)
            project.update({"is_user":0})

        for post in project['post']:
            try:
                Like.objects.get(post_id=post['id'], user_id=request.user.id)
                post.update({"is_liked":1})
            except:
                post.update({"is_liked":0})
            
            try:
                BookMark.objects.get(post_id=post['id'], user_id=request.user.id)
                post.update({"is_marked":1})
            except:
                post.update({"is_marked":0})

        return Response(project, status=status.HTTP_200_OK)

    elif request.method == 'DELETE':
        project_obj = Project.objects.get(id=request.GET['id'])

        for post in Post.objects.filter(project_id=request.GET['id']):
            for image in PostImage.objects.filter(post_id=post.id):
                image.image.delete(save=False)
                
        project_obj.delete()
        return Response("is deleted", status=status.HTTP_200_OK)