from django.contrib.auth.models import User
from django.shortcuts import render

from question_api.models import Question
from user_api.models import Profile

from .serializers import QuestionSerializer, AnswerSerializer, QuestionTagSerialier
from user_api.serializers import ProfileSerializer
from tag.models import Tag, Question_Tag
from tag.serializer import TagSerializer

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
def question_list_load(request):
    if request.method == "GET":

        myQestionModel = Question.objects.filter(user = request.user.id, adopt = False)
        myQuestionSZ = QuestionSerializer(myQestionModel.order_by('-id'), many=True)

        qestionModel = Question.objects.all().order_by('-id')

        page = request.GET.get('page')
        page_obj = Paginator(qestionModel, 5).get_page(page)

        questionSZ = QuestionSerializer(page_obj, many=True)

        return_dict = {
            'my_questions': myQuestionSZ.data,
            'questions': questionSZ.data
            }
        
        for i in myQuestionSZ.data:
            profile_sz = ProfileSerializer(Profile.objects.get(user=i['user']))
            i.update({
                "real_name" : profile_sz.data['real_name'],
                "profile_image" : profile_sz.data['profile_image']
                })

        for i in questionSZ.data:
            profile_sz = ProfileSerializer(Profile.objects.get(user=i['user']))
            i.update({
                "real_name" : profile_sz.data['real_name'],
                "profile_image" : profile_sz.data['profile_image']
                })

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
            if profile_obj.user_id == request.user.id:
                i.update({'is_user':1})
        
        return_dict={
            "real_name": profile_sz_question.data['real_name'],
            "profile_image": profile_sz_question.data['profile_image']
        }
        if qestionModel.user_id == request.user.id:
            return_dict.update({'is_user':1})

        return_dict.update(questionSZ.data)

    return Response(return_dict)


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
        print(question_sz)
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

        Question.objects.filter(id=question_idx).update(adopt=True)


    return Response(answerSZ.data)
