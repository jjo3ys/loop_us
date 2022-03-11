import datetime
from django.db.models import Q
from django.core.paginator import Paginator

from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework import status


from .models import Log, InterestTag#, Connect_log

from post_api.models import Post, Like, BookMark
from post_api.serializers import MainloadSerializer
from project_api.serializers import ProjectSerializer
from user_api.models import Banlist, Profile
from user_api.serializers import ProfileSerializer
from question_api.models import Question
from question_api.serializers import OnlyQSerializer as QuestionSerializer
from tag.models import Project_Tag, Question_Tag
# Create your views here.

# @api_view(['POST'])
# @permission_classes((IsAuthenticated,))
# def connection(request):
#     user_id = request.user.id
#     Connect_log.objects.create(user_id=user_id)
    
#     return Response(status=status.HTTP_200_OK)

# @api_view(['GET'])
# def connection_log(request):
#     date = request.GET['date']
#     sum = Connect_log.objects.all().count()
#     daily = Connect_log.objects.filter(date=date).order_by('user_id')
#     daily_user = daily.values_list('user_id', flat=True).distinct().count()
#     return_dict = {
#         "누적 접속 건수":sum,
#         "{0} 접속 건수".format(date):daily.count(),
#         "{0} 이용자 수".format(date):daily_user
#     }

#     return Response(return_dict, status=status.HTTP_200_OK)
type_int = {'post':1, 'profile':2, 'question':3}    

def interest_tag(interest_list, type, tag, score):
    if type == 'plus':
        try:
            interest_list.tag_list[str(tag)]['count'] += score
            interest_list.tag_list[str(tag)]['date'] = str(datetime.date.today())
        except KeyError:
            interest_list.tag_list[str(tag)] = {'count':score, 'date':str(datetime.date.today()), 'id':tag}
    
    elif type == 'minus':
        try:
            interest_list.tag_list[str(tag)]['count'] -= score
            if interest_list.tag_list[str(tag)]['count'] <= 0:
                del interest_list.tag_list[str(tag)]
        except KeyError:
            pass

    return interest_list

@api_view(['GET', ])
@permission_classes((IsAuthenticated,))
def search(request, type):
    query = request.GET['query']
    page = request.GET['page']
    try:
        ban_list = Banlist.objects.get(user_id=request.user.id).banlist
    except:
        ban_list = []

    ban_list += Banlist.objects.filter(banlist__contains=request.user.id).values_list('user_id', flat=True)

    if type == 'post':
        obj = list(Post.objects.filter(Q(contents__icontains=query)|Q(title__icontains=query)).exclude(user_id__in=ban_list))
        obj.reverse()
        obj = Paginator(obj, 5).get_page(page)
        obj = MainloadSerializer(obj, many=True).data
        for p in obj:
            if request.user.id == p['user_id']:
                p.update({"is_user":1})
            else:
                p.update({"is_user":0})
                
            if Like.objects.filter(user_id=request.user.id, post_id=p['id']).exists():          
                p.update({"is_liked":1})
            else:
                p.update({"is_liked":0})

            if BookMark.objects.filter(user_id=request.user.id, post_id=p['id']).exists():              
                p.update({"is_marked":1})
            else:
                p.update({"is_marked":0})

    elif type == 'profile':
        obj = list(Profile.objects.filter(real_name__icontains=query).exclude(user_id__in=ban_list))
        obj.reverse()
        obj = Paginator(obj, 10).get_page(page)
        obj = ProfileSerializer(obj, many=True).data

    elif type == 'question':
        obj = list(Question.objects.filter(content__icontains=query).exclude(user_id__in=ban_list))
        obj.reverse()
        obj = Paginator(obj, 5).get_page(page)
        obj = QuestionSerializer(obj, many=True).data

    elif type == 'tag_project':
        obj = list(Project_Tag.objects.filter(tag_id=int(query)))
        obj.reverse()
        result = []
        for o in obj:
            if o.project.user_id not in ban_list and o.project not in result:
                result.append(o.project)
        result.reverse()
        obj = ProjectSerializer(result[(int(page)-1)*5:int(page)*5], many=True).data
        for p in obj:
            if request.user.id == p['user_id']:
                p.update({"is_user":1})
            else:
                p.update({"is_user":0})
  
    elif type == 'tag_question':
        obj = list(Question_Tag.objects.filter(tag_id=int(query)))
        obj.reverse()
        result = []
        for o in obj:
            if o.question.user_id not in ban_list and o.question not in result:
                result.append(o.question)
        result.reverse()
        obj = QuestionSerializer(result[(int(page)-1)*5:int(page)*5], many=True).data
        for q in obj:
            if request.user.id == q['user_id']:
                q.update({"is_user":1})
            else:
                q.update({"is_user":0})

    elif type == 'notice':
        return Response("unrealized", status=status.HTTP_204_NO_CONTENT)
    
    if page == '1':
        if 'tag' in type:
            interest_list = InterestTag.objects.get_or_create(user_id=request.user.id)[0]
            interest_list = interest_tag(interest_list, 'plus', int(query), 1)
            interest_list.save()
        else:         
            Log.objects.create(user_id=request.user.id, query=query, type=type_int[type])

    
    return Response(obj, status=status.HTTP_200_OK)

