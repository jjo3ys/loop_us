from question_api.models import Answer, Question#, P2PAnswer, P2PQuestion
from user_api.models import Profile
from user_api.serializers import SimpleProfileSerializer
from fcm.models import FcmToken
from fcm.push_fcm import answer_fcm, adopt_fcm

from .serializers import QuestionSerializer, AnswerSerializer, QuestionTagSerialier, OnlyQSerializer#, P2PAnswerSerializer, P2PQuestionSerializer
from tag.models import Tag, Question_Tag

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

# @api_view(['POST', ])
# @permission_classes((IsAuthenticated,))
# def question_to(request, to_idx):
#     q_obj = P2PQuestion.objects.create(user=request.user,
#                                        to_id=to_idx,
#                                        content=request.data['content'])
    
#     return Response(P2PQuestionSerializer(q_obj).data, status=status.HTTP_200_OK)

@api_view(['GET', ])
@permission_classes((IsAuthenticated,))
def question_list_load(request, type):   
    user_id = request.user.id

    if type == 'my':
        if request.GET['last'] == '0':
            q_obj = list(Question.objects.filter(user = user_id))[-5:]
        else:
            q_obj = list(Question.objects.filter(id__lt=request.GET['last'], user = user_id))[-5:]
        q_obj.reverse()

        q_sz = OnlyQSerializer(q_obj, many = True)
        profile_sz = SimpleProfileSerializer(Profile.objects.get(user = user_id))
        for d in q_sz.data:
            d.update(profile_sz.data)
            d.update({"is_user":1})

    elif type == "any":
        if request.GET['last'] == '0':
            q_obj = list(Question.objects.all())[-5:]
        else:
            q_obj = list(Question.objects.filter(id__lt=request.GET['last']))[-5:]  
        q_obj.reverse()
        
        q_sz = OnlyQSerializer(q_obj, many=True)
        for d in q_sz.data:
            profile_sz = SimpleProfileSerializer(Profile.objects.get(user=d['user_id']))
            d.update(profile_sz.data)
            if d['user_id'] == user_id:
                d.update({"is_user":1})
            else:
                d.update({"is_user":0})

    return Response(q_sz.data, status=status.HTTP_200_OK)


@api_view(['GET', ])
@permission_classes((IsAuthenticated,))
def specific_question_load(request, question_idx):
    user_id = request.user.id

    q_obj = Question.objects.get(id=question_idx)
    q_sz = QuestionSerializer(q_obj).data
    q_profile_obj = Profile.objects.get(user=q_sz['user_id'])
    q_profile_sz = SimpleProfileSerializer(q_profile_obj)
    q_sz.update(q_profile_sz.data)
    if q_obj.adopt:
        q_sz.update({"is_adopted":1})
    else:
        q_sz.update({"is_adopted":0})

    if user_id == q_profile_sz.data['user_id']:
        q_sz.update({"is_user":1})
    else:
        q_sz.update({"is_user":0})

    for d in q_sz['answer']:
        a_profile_obj = Profile.objects.get(user=d['user_id'])
        a_profile_sz = SimpleProfileSerializer(a_profile_obj)
        d.update(a_profile_sz.data)
        if a_profile_obj.user_id == user_id:
            d.update({'is_user':1})
        else:
            d.update({"is_user":0})

    return Response(q_sz, status=status.HTTP_200_OK)

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

# @api_view(['POST', ])
# @permission_classes((IsAuthenticated,))
# def question_to_update(request, question_idx):
#     question_obj = P2PQuestion.objects.get(id=question_idx)
#     question_obj.content = request.data['content']
#     question_obj.save()

#     return Response(P2PQuestionSerializer(question_obj).data, status=status.HTTP_200_OK)

@api_view(['POST', ])
@permission_classes((IsAuthenticated,))
def question_delete(request, question_idx):
    if request.method == "POST":
        try:
            QuestionModel = Question.objects.get(id = question_idx)
            q_tag = Question_Tag.objects.filter(question_id=question_idx)
            for tag in q_tag:
                tag.tag.count = tag.tag.count-1
                tag.tag.save()
                
            if QuestionModel.user.id == request.user.id :
                QuestionModel.delete()
            else:
                return Response('No permission to modify')

        except:
            return Response('Question not found')


    return Response(status=status.HTTP_200_OK)

@api_view(['POST', ])
@permission_classes((IsAuthenticated,))
def answer_adopt(request, answer_id):
    answer_obj = Answer.objects.get(id=answer_id)
    answer_obj.adopt = True
    answer_obj.question.adopt = True
    answer_obj.save()
    try:
        token = FcmToken.objects.get(user_id=answer_obj.user_id)
        adopt_fcm(token)
    except:
        pass
    
    return Response(status=status.HTTP_200_OK)

# @api_view(['POST', ])
# @permission_classes((IsAuthenticated,))
# def question_to_delete(request, question_idx):
#     q_obj = P2PQuestion.objects.get(id=question_idx)
#     q_obj.delete()

#     return Response(status=status.HTTP_200_OK)

@api_view(['POST', ])
@permission_classes((IsAuthenticated,))
def answer(request, question_idx):
    profile_obj = Profile.objects.get(user=request.user.id)
    profile_sz = SimpleProfileSerializer(profile_obj)

    answer_obj = Answer.objects.create(user_id=request.user.id,
                                        question_id=question_idx,
                                        content=request.data['content'],
                                        adopt=False)
    try:
        token = FcmToken.objects.get(user_id=answer_obj.question.user_id)
        answer_fcm(token.token, profile_obj.real_name)
    except:
        pass

    answerSZ = AnswerSerializer(answer_obj)
    data = answerSZ.data
    data.update(profile_sz.data)

    return Response(data, status=status.HTTP_200_OK)

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

    