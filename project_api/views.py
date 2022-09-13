from search.models import Get_log

from .serializers import ProjectPostSerializer
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
    if request.method == 'POST':
        user = request.user
        project_obj = Project.objects.create(user=user, project_name = request.data['project_name'])

        return Response(ProjectPostSerializer(project_obj).data, status=status.HTTP_201_CREATED)

    elif request.method == 'PUT':
        type = request.GET['type']
        project_obj = Project.objects.filter(id=request.GET['id'])[0]
        if type == 'project_name':
            project_obj.project_name = request.data['project_name']

        elif type == 'looper':
            profile_obj = Profile.objects.filter(user_id=request.user.id)[0]
            looper_list = eval(request.data['looper'])

            old_looper = ProjectUser.objects.filter(project_id=project_obj.id)
            for looper in old_looper:
                if looper.looper.id not in looper_list:
                    looper.delete()

            for looper in looper_list:
                looper, created = ProjectUser.objects.get_or_create(project_id=project_obj.id, looper_id=looper)
                if created:
                    try:
                        # token = FcmToken.objects.filter(user_id=looper.looper_id)[0]
                        tag_fcm(looper, profile_obj.real_name, request.user.id, project_obj.project_name, project_obj.id)
                    except:
                        pass
            
        project_obj.save()
        return Response(status=status.HTTP_200_OK)

    # elif request.method == 'GET':
    #     try:
    #         project_obj = Project.objects.filter(id=request.GET['id'])[0]
    #     except IndexError:
    #         return Response(status=status.HTTP_404_NOT_FOUND)

    #     project = ProjectPostSerializer(project_obj).data
    #     if request.user.id == project_obj.user_id:
    #         project.update({"is_user":1})
    #     else:
    #         # Get_log.objects.create(user_id=request.user.id, target_id=request.GET['id'], type=3)
    #         project.update({"is_user":0})

    #     for post in project['post']:
    #         try:
    #             Like.objects.filter(post_id=post['id'], user_id=request.user.id)[0]
    #             post.update({"is_liked":1})
    #         except:
    #             post.update({"is_liked":0})
            
    #         try:
    #             BookMark.objects.filter(post_id=post['id'], user_id=request.user.id)[0]
    #             post.update({"is_marked":1})
    #         except:
    #             post.update({"is_marked":0})

    #     return Response(project, status=status.HTTP_200_OK)

    elif request.method == 'DELETE':
        project_obj = Project.objects.filter(id=request.GET['id'])[0]

        for post in Post.objects.filter(project_id=request.GET['id']):
            for image in PostImage.objects.filter(post_id=post.id):
                image.image.delete(save=False)
                
        project_obj.delete()
        return Response("is deleted", status=status.HTTP_200_OK)