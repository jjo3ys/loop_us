from django.shortcuts import render
from django.db.models import Q
from django.core.paginator import Paginator

from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework import status

from .models import Log

from post_api.models import Post
from post_api.serializers import PostingSerializer
from project_api.models import Project
from project_api.serializers import ProjectSerializer
from user_api.models import Profile
from user_api.serializers import ProfileSerializer
from question_api.models import Question, Answer
from question_api.serializers import QuestionSerializer, AnswerSerializer
# Create your views here.

@api_view(['GET', ])
@permission_classes((IsAuthenticated,))
def log(request, type):
    user_id = request.user.id
    query = request.GET['query']
    Log.objects.create(user_id=user_id, query=query)
    if type == 'post':
        obj = Post.objects.filter(Q(content__icontains=query)|Q(title__icontains=query)).order_by('-id')
        obj = Paginator(obj, 5).get_page(1)
        return Response(PostingSerializer(obj, many=True).data, status=status.HTTP_200_OK)

    elif type == 'project':
        obj = Project.objects.filter(Q(project_name__icontains=query)|Q(introduction__icontains=query)).order_by('-id')
        obj = Paginator(obj, 5).get_page(1)
        return Response(ProjectSerializer(obj, many=True).data, status=status.HTTP_200_OK)  

    elif type == 'profile':
        obj = Profile.objects.filter(real_name__icontains=query).order_by('-id')
        obj = Paginator(obj, 5).get_page(1)
        return Response(ProfileSerializer(obj, many=True).data, status=status.HTTP_200_OK)  

    elif type == 'question':
        obj = Question.objects.filter(content__icontains=query).order_by('-id')
        obj = Paginator(obj, 5).get_page(1)
        return Response(QuestionSerializer(obj, many=True).data, status=status.HTTP_200_OK)  

    elif type == 'notice':
        return Response("unrealized", status=status.HTTP_204_NO_CONTENT)

@api_view(['GET', ])
@permission_classes((IsAuthenticated,))
def search(request, type):
    query = request.GET['query']
    page = request.GET['page']

    if type == 'post':
        obj = Post.objects.filter(Q(content__icontains=query)|Q(title__icontains=query)).order_by('-id')
        obj = Paginator(obj, 5).get_page(page)
        return Response(PostingSerializer(obj, many=True).data, status=status.HTTP_200_OK)

    elif type == 'project':
        obj = Project.objects.filter(Q(project_name__icontains=query)|Q(introduction__icontains=query)).order_by('-id')
        obj = Paginator(obj, 5).get_page(page)
        return Response(ProjectSerializer(obj, many=True).data, status=status.HTTP_200_OK)  

    elif type == 'profile':
        obj = Profile.objects.filter(real_name__icontains=query).order_by('-id')
        obj = Paginator(obj, 5).get_page(page)
        return Response(ProfileSerializer(obj, many=True).data, status=status.HTTP_200_OK)  

    elif type == 'question':
        obj = Question.objects.filter(content__icontains=query).order_by('-id')
        obj = Paginator(obj, 5).get_page(page)
        return Response(QuestionSerializer(obj, many=True).data, status=status.HTTP_200_OK)  

    elif type == 'notice':
        return Response("unrealized", status=status.HTTP_204_NO_CONTENT)