import datetime

from search.models import InterestTag
from .serializers import ProjectPostSerializer
from .models import Project, TagLooper
from tag.models import Tag, Project_Tag
from user_api.models import Profile
from user_api.serializers import SimpleProfileSerializer
from fcm.models import FcmToken
from fcm.push_fcm import tag_fcm
from post_api.models import Like, BookMark

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
                                            end_date = end_date,
                                            pj_thumbnail = request.FILES.get('thumbnail'))
        
        for looper in eval(request.data['looper']):
            TagLooper.objects.create(project=project_obj, looper_id=looper)
            try:
                token = FcmToken.objects.get(user_id=looper)
                tag_fcm(token.token, profile_obj.real_name)
            except:
                pass

        interest_list = InterestTag.objects.get_or_create(user_id=user.id)[0]
        for tag in eval(request.data['tag']):
            tag_obj, valid = Tag.objects.get_or_create(tag=tag)
            try:
                interest_list.tag_list[str(tag_obj.id)]['count'] += 1
                interest_list.tag_list[str(tag.id)]['date'] = str(datetime.date.today())
            except KeyError:
                interest_list.tag_list[str(tag_obj.id)] = {'count':1, 'date':str(datetime.date.today())}

            if not valid:
                tag_obj.count = tag_obj.count + 1
                tag_obj.save()
            
            Project_Tag.objects.create(project=project_obj, tag=tag_obj)

        interest_list.save()
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

        elif type =='thumbnail':
            project_obj.pj_thumbnail = request.FILES.get('thumbnail') 

        elif type == 'tag':   
            interest_list = InterestTag.objects.get_or_create(user_id=request.user.id)[0] 
            old_tag = Project_Tag.objects.filter(project_id=project_obj.id)
            for tag in old_tag:
                try:
                    interest_list.tag_list[str(tag.tag.id)]['count'] -= 1
                    if interest_list.tag_list[str(tag.tag.id)]['count'] == 0:
                        del interest_list.tag_list[str(tag.tag.id)]
                except KeyError:
                    pass

                tag.delete()
                tag.tag.count = tag.tag.count-1
                if tag.tag.count == 0:
                    tag.tag.delete()

            tag_list = eval(request.data['tag'])      
            for tag in tag_list:
                tag, valid = Tag.objects.get_or_create(tag=tag)
                try:
                    interest_list.tag_list[str(tag.id)]['count'] += 1
                    interest_list.tag_list[str(tag.id)]['date'] = str(datetime.date.today())
                except KeyError:
                    interest_list.tag_list[str(tag.id)] = {'count':1, 'date':str(datetime.date.today())}

                Project_Tag.objects.create(tag = tag, project_id = project_obj.id)
                if not valid:
                    tag.count = tag.count+1
                    tag.save()

            interest_list.save()

        elif type == 'looper':
            profile_obj = Profile.objects.get(user_id=request.user.id)
            looper_list = eval(request.data['looper'])
            old_looper = TagLooper.objects.filter(project_id=project_obj.id)
            for looper in old_looper:
                if looper.looper.id not in looper_list:
                    looper.delete()

            for looper in looper_list:
                looper, valid = TagLooper.objects.get_or_create(project_id=project_obj.id, looper_id=looper)
                if valid:
                    try:
                        token = FcmToken.objects.get(user_id=looper.looper_id)
                        tag_fcm(token.token, profile_obj.real_name)
                    except:
                        pass
            
        project_obj.save()
        return Response(status=status.HTTP_200_OK)

    elif request.method == 'GET':
        project_obj = Project.objects.get(id=request.GET['id'])
        project = ProjectPostSerializer(project_obj).data
        profile_obj = Profile.objects.get(user=project_obj.user)
        profile_obj = SimpleProfileSerializer(profile_obj).data
        project.update(profile_obj)
        if request.user.id == project_obj.user_id:
            project.update({"is_user":1})
        else:
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
        interest_list = InterestTag.objects.get_or_create(user_id=request.user.id)
        project_tag = Project_Tag.objects.filter(project_id=request.GET['id'])
        for tag in project_tag:
            try:
                interest_list.tag_list[str(tag.tag.id)]['count'] -= 1
                if interest_list.tag_list[str(tag.tag.id)]['count'] == 0:
                    del interest_list.tag_list[str(tag.tag.id)]
            except KeyError:
                pass

            tag.tag.count = tag.tag.count-1
            if tag.tag.count == 0:
                tag.tag.save()
            else:
                tag.tag.save()

        interest_list.save()
        project_obj.delete()
        return Response("is deleted", status=status.HTTP_200_OK)