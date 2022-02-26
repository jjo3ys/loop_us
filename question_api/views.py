import datetime
from question_api.models import Answer, Question
from search.models import Get_log, InterestTag
from search.views import interest_tag#, P2PAnswer, P2PQuestion
from user_api.models import Profile, Report
from fcm.models import FcmToken
from fcm.push_fcm import answer_fcm, report_alarm

from .serializers import QuestionSerializer, AnswerSerializer, OnlyQSerializer#, P2PAnswerSerializer, P2PQuestionSerializer
from tag.models import Tag, Question_Tag

from rest_framework import status
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated

# Create your views here.


@api_view(['POST', 'GET', 'PUT', 'DELETE'])
@permission_classes((IsAuthenticated,))
def question(request):
    user_id = request.user.id
    if request.method == "POST":
        question_obj = Question.objects.create(user_id=user_id,
                                               content=request.data['content'],
                                               adopt=False)

        interest_list = InterestTag.objects.get_or_create(user_id=user_id)[0]
        for tag in request.data['tag']:
            tag_obj, valid = Tag.objects.get_or_create(tag=tag)
            interest_list = interest_tag(interest_list, 'plus', tag.id, 20) 

            if not valid:
                tag_obj.count = tag_obj.count + 1
                tag_obj.save() 
             
            Question_Tag.objects.create(question=question_obj, tag=tag_obj)

        interest_list.save()
        return Response(status=status.HTTP_200_OK)
    
    elif request.method == 'GET':   
        try:  
            q_obj = Question.objects.get(id=request.GET['id'])
        except Question.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)

        q_sz = QuestionSerializer(q_obj).data

        if user_id == q_obj.user_id:
            q_sz.update({"is_user":1})
        else:
            Get_log.objects.create(user_id=user_id, target_id=request.GET['id'], type=2)
            q_sz.update({"is_user":0})

        for d in q_sz['answer']:
            if d['user_id'] == user_id:
                d.update({'is_user':1})
            else:
                d.update({"is_user":0})

        return Response(q_sz, status=status.HTTP_200_OK)          
    
    elif request.method == 'PUT':
        question_obj = Question.objects.get(id=request.GET['id'])
        question_obj.content = request.data['content']
        question_obj.save()

        interest_list = InterestTag.objects.get_or_create(user_id=user_id)[0]
        old_tag = Question_Tag.objects.filter(question_id=request.GET['id'])
        for tag in old_tag:
            interest_list = interest_tag(interest_list, 'minus', tag.tag_id, 20)
            tag.delete()
            tag.tag.count = tag.tag.count-1
            if tag.tag.count == 0:
                tag.tag.delete()

        tag_list = eval(request.data['tag'])      
        for tag in tag_list:
            tag, valid = Tag.objects.get_or_create(tag=tag)
            Question_Tag.objects.create(tag = tag, question_id = question_obj.id)
            interest_list = interest_tag(interest_list, 'plus', tag.tag_id, 20)

            if not valid:
                tag.count = tag.count+1
                tag.save()

        interest_list.save()
        question_sz = QuestionSerializer(question_obj)
        return Response(question_sz.data, status=status.HTTP_200_OK)

    elif request.method == 'DELETE':
        try:
            interest_list = InterestTag.objects.get_or_create(user_id=user_id)[0]
            QuestionModel = Question.objects.get(id = request.GET['id'])
            q_tag = Question_Tag.objects.filter(question_id=request.GET['id'])
            for tag in q_tag:
                interest_list = interest_tag(interest_list, 'minus', tag.tag_id, 20)
                tag.tag.count = tag.tag.count-1
                if tag.tag.count == 0:
                    tag.tag.delete()
                else:
                    tag.tag.save()
                
            interest_list.save()
            QuestionModel.delete()
        
        except:
            return Response(status=status.HTTP_404_NOT_FOUND)


    return Response(status=status.HTTP_200_OK)

@api_view(['GET', ])
@permission_classes((IsAuthenticated,))
def question_list(request, type):   
    user_id = request.user.id

    if type == 'my':
        try:
            if request.GET['last'] == '0':
                q_obj = list(Question.objects.filter(user = user_id))[-5:]
            else:
                q_obj = list(Question.objects.filter(id__lt=request.GET['last'], user = user_id))[-5:]
            q_obj.reverse()
        except Question.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)

        q_sz = OnlyQSerializer(q_obj, many = True)
        for d in q_sz.data:
            d.update({"is_user":1})

    elif type == "any":
        try:
            if request.GET['last'] == '0':
                q_obj = list(Question.objects.all())[-5:]
            else:
                q_obj = list(Question.objects.filter(id__lt=request.GET['last']))[-5:]  
            q_obj.reverse()
        except Question.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)

        q_sz = OnlyQSerializer(q_obj, many=True)
        for d in q_sz.data:
            if d['user_id'] == user_id:
                d.update({"is_user":1})
            else:
                d.update({"is_user":0})

    return Response(q_sz.data, status=status.HTTP_200_OK)

@api_view(['POST', 'PUT', 'DELETE'])
@permission_classes((IsAuthenticated,))
def answer(request, question_idx):
    if request.method == 'POST':
        try:
            answer_obj = Answer.objects.create(user_id=request.user.id,
                                                question_id=question_idx,
                                                content=request.data['content'],
                                                adopt=False)
        except:
            return Response(status=status.HTTP_404_NOT_FOUND)
        if answer_obj.question.user_id != request.user.id:
            try:
                questioner_id = answer_obj.question.user_id
                token = FcmToken.objects.get(user_id=questioner_id)
                answer_fcm(token, request.user.id, answer_obj.question.content, question_idx, Profile.objects.get(user_id=questioner_id).real_name)
            except FcmToken.DoesNotExist:
                pass

        return Response(AnswerSerializer(answer_obj).data, status=status.HTTP_200_OK)
    
    elif request.method == "PUT":
        answer = Answer.objects.get(id=request.GET['id'])
        answer.content = request.data['content']
        answer.save()
        return Response(AnswerSerializer(answer).data, status=status.HTTP_200_OK)

    elif request.method == 'DELETE':
        Answer.objects.get(id=request.GET['id']).delete()
        return Response(status=status.HTTP_200_OK)

@api_view(['POST', ])
@permission_classes((IsAuthenticated,))
def report(request):
    Report.objects.create(user_id=request.user.id, type=2, target_id=request.data['id'], reason=request.data['reason'])
    count = Report.objects.filter(type=2, target_id=request.data['id']).count()
    if count >= 3:
        report_alarm(count, 2, request.data['id'], request.data['reason'])
        return Response(status=status.HTTP_200_OK)

@api_view(['POST', ])
@permission_classes((IsAuthenticated,))
def answer_report(request):
    Report.objects.create(user_id=request.user.id, type=3, target_id=request.data['id'], reason=request.data['reason'])
    count = Report.objects.filter(type=3, target_id=request.data['id']).count()
    if count >= 3:
        report_alarm(count, 3, request.data['id'], request.data['reason'])
        return Response(status=status.HTTP_200_OK)
    # @api_view(['POST', ])
# @permission_classes((IsAuthenticated,))
# def question_to(request, to_idx):
#     q_obj = P2PQuestion.objects.create(user=request.user,
#                                        to_id=to_idx,
#                                        content=request.data['content'])
    
#     return Response(P2PQuestionSerializer(q_obj).data, status=status.HTTP_200_OK)

# @api_view(['GET', ])
# @permission_classes((IsAuthenticated,))
# def question_to_load(request, question_idx):
#     user_id = request.user.id

#     q_obj = P2PQuestion.objects.get(id=question_idx)
#     data = P2PQuestionSerializer(q_obj).data

#     if user_id == data['user_profile']['user_id']:
#         data.update({"is_user":1})
#     else:
#         data.update({"is_user":0})

#     if user_id == data['to_profile']['user_id']:
#         data.update({"is_to":1})
#     else:
#         data.update({"is_to":0})

#     for d in data['p2panswer']:
#         if d['user_profile']['user_id'] == user_id:
#             d.update({'is_user':1})
#         else:
#             d.update({"is_user":0})

#     return Response(data, status=status.HTTP_200_OK)
# @api_view(['POST', ])
# @permission_classes((IsAuthenticated,))
# def question_to_update(request, question_idx):
#     question_obj = P2PQuestion.objects.get(id=question_idx)
#     question_obj.content = request.data['content']
#     question_obj.save()

#     return Response(P2PQuestionSerializer(question_obj).data, status=status.HTTP_200_OK)


# @api_view(['POST', ])
# @permission_classes((IsAuthenticated,))
# def question_to_delete(request, question_idx):
#     q_obj = P2PQuestion.objects.get(id=question_idx)
#     q_obj.delete()

#     return Response(status=status.HTTP_200_OK)



# @api_view(['POST', ])
# @permission_classes((IsAuthenticated,))
# def answer_to(request, question_idx):
#     answer_obj = P2PAnswer.objects.create(user=request.user,
#                                           question_id = question_idx,
#                                           content=request.data['content'])
#     answer = P2PAnswerSerializer(answer_obj).data
    
#     try:
#         token = FcmToken.objects.get(user_id=answer_obj.question.user_id)
#         answer_fcm(token.token, answer['user_profile']['real_name'])
#     except:
#         pass

#     return Response(answer, status=status.HTTP_200_OK)

    