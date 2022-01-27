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
from user_api.models import Profile
from user_api.serializers import ProfileSerializer, SimpleProfileSerializer
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
    
@api_view(['GET', ])
@permission_classes((IsAuthenticated,))
def search(request, type):
    query = request.GET['query']
    page = request.GET['page']
    if page == 1:
        if 'tag' in type:
            interest_list = InterestTag.objects.get_or_create(user_id=request.user.id)[0]
            try:
                interest_list.tag_list[query]['count'] += 1
                interest_list.tag_list[query]['date'] = datetime.date.today()
            except KeyError:
                interest_list.tag_list[query] = {'count':1, 'date':datetime.date.today()}
            
            interest_list.save()

        else:
            Log.objects.create(user_id=request.user.id, query=query)

    if type == 'post':
        obj = list(Post.objects.filter(Q(contents__icontains=query)|Q(title__icontains=query)))
        obj.reverse()
        post_obj = Paginator(obj, 5).get_page(page)
        post_obj = MainloadSerializer(post_obj, many=True).data
        for p in post_obj:
            p.update(SimpleProfileSerializer(Profile.objects.get(user_id=p['user_id'])).data)
            if request.user.id == p['user_id']:
                p.update({"is_user":1})
            else:
                p.update({"is_user":0})
                
            try:
                Like.objects.get(user_id=request.user.id, post_id=p['id'])
                p.update({"is_liked":1})
            except:
                p.update({"is_liked":0})

            try:
                BookMark.objects.get(user_id=request.user.id, post_id=p['id'])
                p.update({"is_marked":1})
            except:
                p.update({"is_marked":0})

        return Response(post_obj, status=status.HTTP_200_OK)

    elif type == 'profile':
        obj = Profile.objects.filter(real_name__icontains=query).order_by('-id')
        obj = Paginator(obj, 10).get_page(page)
        return Response(ProfileSerializer(obj, many=True).data, status=status.HTTP_200_OK)  

    elif type == 'question':
        obj = Question.objects.filter(content__icontains=query).order_by('-id')
        obj = Paginator(obj, 5).get_page(page)
        obj = QuestionSerializer(obj, many=True).data
        for q in obj:
            q.update(SimpleProfileSerializer(Profile.objects.get(user_id=q['user_id'])).data)

        return Response(obj, status=status.HTTP_200_OK)  

    elif type == 'tag_project':
        obj = list(Project_Tag.objects.filter(tag_id=int(query)))
        obj.reverse()
        obj = Paginator(obj, 5).get_page(page)
        result = []
        for o in obj:
            if o.project not in result:
                result.append(o.project)
        result.reverse()
        obj = ProjectSerializer(result, many=True).data
        for p in obj:
            p.update(SimpleProfileSerializer(Profile.objects.get(user_id=p['user_id'])).data)
            if request.user.id == p['user_id']:
                p.update({"is_user":1})
            else:
                p.update({"is_user":0})

        return Response(obj, status=status.HTTP_200_OK)
    
    elif type == 'tag_question':
        obj = list(Question_Tag.objects.filter(tag_id=int(query)))
        obj.reverse()
        obj = Paginator(obj, 5).get_page(page)
        result = []
        for o in obj:
            if o.question not in result:
                result.append(o.question)
        result.reverse()
        obj = QuestionSerializer(result, many=True).data
        for q in obj:
            q.update(SimpleProfileSerializer(Profile.objects.get(user_id=q['user_id'])).data)
            if request.user.id == q['user_id']:
                q.update({"is_user":1})
            else:
                q.update({"is_user":0})

        return Response(obj, status=status.HTTP_200_OK)


    elif type == 'notice':
        return Response("unrealized", status=status.HTTP_204_NO_CONTENT)