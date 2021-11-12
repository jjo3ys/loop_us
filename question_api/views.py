from django.shortcuts import render

from question_api.models import Question

from .serializers import QuestionSerializer, AnswerSerializer

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
            return Response('유효하지 않은 형식입니다.', status=status.HTTP_404_NOT_FOUND)

    return Response(questionSZ.data)


@api_view(['GET', ])
@permission_classes((IsAuthenticated,))
def question_list_load(request):
    if request.method == "GET":
        qestionModel = Question.objects.all().order_by('-id')
        questionSZ = QuestionSerializer(qestionModel, many=True)

    return Response(questionSZ.data)


@api_view(['GET', ])
@permission_classes((IsAuthenticated,))
def specific_question_load(request, question_idx):
    if request.method == "GET":
        qestionModel = Question.objects.get(id=question_idx)
        questionSZ = QuestionSerializer(qestionModel)

    return Response(questionSZ.data)


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
