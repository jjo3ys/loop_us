from django.shortcuts import render
from django.db.models import Q
from django.core.paginator import Paginator

from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework import status

from .models import Log

from post_api.models import Post, Like, BookMark
from post_api.serializers import SimpleProjectserializer, MainloadSerializer
from project_api.serializers import ProjectSerializer
from user_api.models import Profile
from user_api.serializers import ProfileSerializer, SimpleProfileSerializer
from question_api.models import Question
from question_api.serializers import OnlyQSerializer as QuestionSerializer
from tag.models import Project_Tag, Question_Tag
# Create your views here.

@api_view(['GET', ])
@permission_classes((IsAuthenticated,))
def search(request, type):
    query = request.GET['query']
    page = request.GET['page']
    if page == 1:
        Log.objects.create(user_id=request.user.id, query=query)

    if type == 'post':
        obj = Post.objects.filter(Q(contents__icontains=query)|Q(title__icontains=query)).order_by('-id')
        post_obj = Paginator(obj, 5).get_page(page)
        data_list = MainloadSerializer(post_obj, many=True).data
        for i in range(len(data_list)):
            profile = Profile.objects.get(user=obj[i].user)
            data_list[i].update(SimpleProjectserializer(obj[i].project).data)
            data_list[i].update(SimpleProfileSerializer(profile).data)
            try:
                Like.objects.get(user_id=request.user.id, post_id=post_obj[i].id)
                data_list[i].update({"is_liked":1})
            except:
                data_list[i].update({"is_liked":0})

            try:
                BookMark.objects.get(user_id=request.user.id, post_id=post_obj[i].id)
                data_list[i].update({"is_marked":1})
            except:
                data_list[i].update({"is_marked":0})

        return Response(data_list, status=status.HTTP_200_OK)

    elif type == 'profile':
        obj = Profile.objects.filter(real_name__icontains=query).order_by('-id')
        obj = Paginator(obj, 10).get_page(page)
        return Response(ProfileSerializer(obj, many=True).data, status=status.HTTP_200_OK)  

    elif type == 'question':
        obj = Question.objects.filter(content__icontains=query).order_by('-id')
        obj = Paginator(obj, 5).get_page(page)
        data_list = QuestionSerializer(obj, many=True).data
        for i in range(len(data_list)):
            profile = Profile.objects.get(user=obj[i].user)
            data_list[i].update(SimpleProfileSerializer(profile).data)
        return Response(data_list, status=status.HTTP_200_OK)  

    elif type == 'tag_project':
        obj = Project_Tag.objects.filter(tag_id=int(query)).order_by('-id')
        obj = Paginator(obj, 5).get_page(page)
        result = []
        for o in obj:
            if o.project not in result:
                result.append(o.project)
        result.reverse()
        data_list = ProjectSerializer(result, many=True).data
        for i in range(len(result)):
            try:
                profile = Profile.objects.get(user_id=data_list[i]['user_id'])
                data_list[i].update(SimpleProfileSerializer(profile).data)
            except Profile.DoesNotExist:
                data_list[i].update({"real_name":"DoesNotExist",
                                     "profile_image":None,
                                     "department":"DoesNotExist"})
        return Response(data_list, status=status.HTTP_200_OK)
    
    elif type == 'tag_question':
        obj = Question_Tag.objects.filter(tag_id=int(query)).order_by('-id')
        obj = Paginator(obj, 5).get_page(page)
        result = []
        for o in obj:
            if o.question not in result:
                result.append(o.question)
        result.reverse()
        data_list = QuestionSerializer(result, many=True).data
        for i in range(len(result)):
            try:
                profile = Profile.objects.get(user_id=data_list[i]['user_id'])
                data_list[i].update(SimpleProfileSerializer(profile).data)
            except Profile.DoesNotExist:
                data_list[i].update({"real_name":"DoesNotExist",
                                     "profile_image":None,
                                     "department":"DoesNotExist"})
        return Response(data_list, status=status.HTTP_200_OK)

    elif type == 'notice':
        return Response("unrealized", status=status.HTTP_204_NO_CONTENT)