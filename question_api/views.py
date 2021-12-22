from django.shortcuts import render

from question_api.models import Answer, Question
from user_api.models import Profile
from user_api.serializers import SimpleProfileSerializer as ProfileSerializer

from .serializers import QuestionSerializer, AnswerSerializer, QuestionTagSerialier, OnlyQSerializer
from tag.models import Tag, Question_Tag

from django.core.paginator import Paginator

from rest_framework import status
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated

# Create your views here.


@api_view(['POST', ])
@permission_classes((IsAuthenticated,))
def raise_question(request):
    if request.method == "POST":
        question_obj = Question.objects.create(user_id=request.user.id,
                                               content=request.data['content'],
                                               adopt=False)
        
        for tag in request.data['tag']:
            try: 
                tag_obj = Tag.objects.get(tag=tag)
                tag_obj.count = tag_obj.count + 1
                tag_obj.save()
            
            except Tag.DoesNotExist:
                tag_obj = Tag.objects.create(tag = tag)
            
            Question_Tag.objects.create(question=question_obj, tag=tag_obj)
        
        questionSZ = QuestionSerializer(question_obj)
        return Response(questionSZ.data)


@api_view(['GET', ])
@permission_classes((IsAuthenticated,))
def question_list_load(request, type):
    page = request.GET.get('page')
    user_id = request.user.id

    if type == 'my':
        q_obj = Question.objects.filter(user = user_id).order_by('-id')
        q_obj = Paginator(q_obj, 5).get_page(page)
        q_sz = OnlyQSerializer(q_obj, many = True)
        profile_sz = ProfileSerializer(Profile.objects.get(user = user_id))
        for d in q_sz.data:
            d.update(profile_sz.data)
            d.update({"is_user":1})

    elif type == "any":
        q_obj = Question.objects.all().order_by('-id')
        page_obj = Paginator(q_obj, 5).get_page(page)
        q_sz = OnlyQSerializer(page_obj, many=True)
        for d in q_sz.data:
            profile_sz = ProfileSerializer(Profile.objects.get(user=d['user_id']))
            d.update(profile_sz.data)
            if d['user_id'] == user_id:
                d.update({"is_user":1})

    return Response(q_sz.data, status=status.HTTP_200_OK)


@api_view(['GET', ])
@permission_classes((IsAuthenticated,))
def specific_question_load(request, question_idx):
    user_id = request.user.id

    q_obj = Question.objects.get(id=question_idx)
    q_sz = QuestionSerializer(q_obj).data
    q_profile_obj = Profile.objects.get(user=q_sz['user_id'])
    q_profile_sz = ProfileSerializer(q_profile_obj)
    q_sz.update(q_profile_sz.data)
    if user_id == q_profile_sz.data['user_id']:
        q_sz.update({"is_user":1})
    
    for d in q_sz['answers']:
        a_profile_obj = Profile.objects.get(user=d['user_id'])
        a_profile_sz = ProfileSerializer(a_profile_obj)
        d.update(a_profile_sz.data)
        if a_profile_obj.user_id == user_id:
            d.update({'is_user':1})

    return Response(q_sz, status=status.HTTP_200_OK)

@api_view(['POST', ])
@permission_classes((IsAuthenticated,))
def question_update(request, question_idx):
    if request.method == "POST":
        question_obj = Question.objects.get(id=question_idx)
        question_obj.content = request.data['content']
        question_obj.save()

        old_tag = Question_Tag.objects.filter(question=question_idx)
        old_sz = QuestionTagSerialier(old_tag, many=True)
        old_list = []
        
        for tag in old_sz.data:
            old_list.append(tag['tag'])

            if tag['tag'] not in request.data['tag']:
                Question_Tag.objects.get(tag_id = tag['tag_id'], question=question_obj).delete()
                tag_obj = Tag.objects.get(id=tag['tag_id'])
                tag_obj.count = tag_obj.count + 1
                if tag_obj.count == 0:
                    tag_obj.delete()
                else:
                    tag_obj.save()
        
        for tag in request.data['tag']:
            if tag in old_list:
                continue
            else:
                try:
                    tag_obj = Tag.objects.get(tag=tag)
                    tag_obj.count = tag_obj.count + 1
                    tag_obj.save()

                except Tag.DoesNotExist:
                    tag_obj = Tag.objects.create(tag = tag)

            Question_Tag.objects.create(tag = tag_obj, project = question_obj)
        
        question_sz = QuestionSerializer(question_obj)

    return Response(question_sz.data, status=status.HTTP_200_OK)


@api_view(['POST', ])
@permission_classes((IsAuthenticated,))
def question_delete(request, question_idx):
    if request.method == "POST":
        try:
            QuestionModel = Question.objects.get(id = question_idx)
            if QuestionModel.user.id == request.user.id :
                QuestionModel.delete()
            else:
                return Response('No permission to modify')
        except:
            return Response('Question not found')


    return Response(status=status.HTTP_200_OK)


@api_view(['POST', ])
@permission_classes((IsAuthenticated,))
def answer(request, question_idx):
    profile_obj = Profile.objects.get(user=request.user.id)
    profile_sz = ProfileSerializer(profile_obj)

    answer_obj = Answer.objects.create(user_id=request.user.id,
                                        question_id=question_idx,
                                        content=request.data['content'],
                                        adopt=False)

    answerSZ = AnswerSerializer(answer_obj)
    data = answerSZ.data
    data.update(profile_sz.data)

    q_obj = Question.objects.get(id=question_idx)
    q_obj.adopt = True
    q_obj.save()

    return Response(data, status=status.HTTP_200_OK)
