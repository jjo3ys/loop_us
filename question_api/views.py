from django.contrib.auth.models import User
from django.shortcuts import render

from question_api.models import Question
from user_api.models import Profile

from .serializers import QuestionSerializer, AnswerSerializer
from user_api.serializers import ProfileSerializer
from tag.serializer import TagSerializer

from rest_framework import status
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated

# Create your views here.


@api_view(['POST', ])
@permission_classes((IsAuthenticated,))
def raise_question(request):
    if request.method == "POST":
        questionSZ = QuestionSerializer(data={
            'user': request.user.id,
            'content': request.data['content'],
            'adopt': False
        })
        if questionSZ.is_valid():
            questionSZ.save()
        else:
            return Response('유효하지 않은 contents 형식입니다.', status=status.HTTP_404_NOT_FOUND)


    return Response(questionSZ.data)


@api_view(['GET', ])
@permission_classes((IsAuthenticated,))
def question_list_load(request):
    if request.method == "GET":
        myQestionModel = Question.objects.filter(user = request.user.id).order_by('-id')
        myQuestionSZ = QuestionSerializer(myQestionModel, many=True)

        qestionModel = Question.objects.all().order_by('-id')
        questionSZ = QuestionSerializer(qestionModel, many=True)


        return_dict = {
            'my_questions': myQuestionSZ.data,
            'questions': questionSZ.data
            }

    return Response(return_dict)


@api_view(['GET', ])
@permission_classes((IsAuthenticated,))
def specific_question_load(request, question_idx):
    if request.method == "GET":
        qestionModel = Question.objects.get(id=question_idx)
        questionSZ = QuestionSerializer(qestionModel)

        profile_obj_question = Profile.objects.get(user=questionSZ.data['user'])
        profile_sz_question = ProfileSerializer(profile_obj_question)
        
        for i in questionSZ.data['answers']:
            profile_obj = Profile.objects.get(user=i['user'])
            profile_sz = ProfileSerializer(profile_obj)
            i.update({
                "real_name" : profile_sz.data['real_name'],
                "profile_image" : profile_sz.data['profile_image']
                })
        
        return_dict={
            "real_name": profile_sz_question.data['real_name'],
            "profile_image": profile_sz_question.data['profile_image']
        }
        return_dict.update(questionSZ.data)

    return Response(return_dict)


@api_view(['POST', ])
@permission_classes((IsAuthenticated,))
def question_update(request):
    if request.method == "POST":
        answerSZ = AnswerSerializer(data={
            'user': request.user.id,
            'content': request.data['content'],
            'adopt': False
        })
        if answerSZ.is_valid():
            answerSZ.save()
        else:
            return Response('유효하지 않은 형식입니다.', status=status.HTTP_404_NOT_FOUND)

    return Response(answerSZ.data)


@api_view(['POST', ])
@permission_classes((IsAuthenticated,))
def question_delete(request):
    if request.method == "POST":
        answerSZ = AnswerSerializer(data={
            'user': request.user.id,
            'content': request.data['content'],
            'adopt': False
        })
        if answerSZ.is_valid():
            answerSZ.save()
        else:
            return Response('유효하지 않은 형식입니다.', status=status.HTTP_404_NOT_FOUND)

    return Response(answerSZ.data)


@api_view(['POST', ])
@permission_classes((IsAuthenticated,))
def answer(request, question_idx):
    if request.method == "POST":
        answerSZ = AnswerSerializer(data={
            'user': request.user.id,
            'question': question_idx,
            'content': request.data['content'],
            'adopt': False
        })
        if answerSZ.is_valid():
            answerSZ.save()
        else:
            return Response('유효하지 않은 형식입니다.', status=status.HTTP_404_NOT_FOUND)

    return Response(answerSZ.data)
