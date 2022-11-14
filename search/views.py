import datetime
from django.core.paginator import Paginator
# from elasticsearch_dsl import Q

from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework import status

# from user_api.builk import ProfileDocument


# from .models import Log, InterestTag#, Connect_log
# from .builk import ProfileDocument

from post_api.models import Post, Like, BookMark
from post_api.serializers import MainloadSerializer
from user_api.models import Banlist, Company, Company_Inform, Profile, School, Department
from user_api.serializers import SchoolSerializer, DepSerializer, SimpleComapnyProfileSerializer, SimpleProfileSerializer, SearchCompanySerializer
from tag.models import Post_Tag

from .models import Log
from .serializer import LogSerializer

from elasticsearch import Elasticsearch

es = Elasticsearch(hosts=['localhost:9200'])

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
type_int = {'post':1, 'profile':2}    

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

@api_view(['GET'])
@permission_classes((IsAuthenticated,))
def search(request, type):
    user_id = request.user.id
    query = request.GET['query']
    page = int(request.GET['page'])

    try:
        ban_list = Banlist.objects.filter(user_id=user_id)[0].banlist
    except:
        ban_list = []

    ban_list += Banlist.objects.filter(banlist__contains=user_id).values_list('user_id', flat=True)

    if type == 'post':
        obj = Post.objects.filter(contents__icontains=query).exclude(user_id__in=ban_list).select_related('project').order_by('-id')
        if obj.count()//20+1 < page:
            return Response(status=status.HTTP_204_NO_CONTENT)
        obj = obj[(page-1)*20:page*20]
        post_list = list(obj.values_list('id', flat=True))
        like_list = dict(Like.objects.filter(user_id=user_id, post_id__in=post_list).values_list('post_id', 'user_id'))
        book_list = dict(BookMark.objects.filter(user_id=user_id, post_id__in=post_list).values_list('post_id', 'user_id'))
        obj = MainloadSerializer(obj, many=True).data

        for p in obj:
            if p['user_id'] == user_id:
                p.update({"is_user":1})
            else:
                p.update({"is_user":0})
            
            if p['id'] in like_list:
                p.update({'is_liked':1})
            else:
                p.update({'is_liked':0})

            if p['id'] in book_list:
                p.update({'is_marked':1})
            else:
                p.update({'is_marked':0})

    elif type == 'profile':
        results = es.search(index='profile', body={'query':{'match':{"text":{"query":query, "analyzer":"ngram_analyzer"}}}}, size=1000)['hits']['hits'][(page-1)*20:page*20]
        if len(results) == 0:
            return Response(status=status.HTTP_204_NO_CONTENT)
        results = list(map(lambda x: Profile.objects.filter(user_id= x['_source']['user_id'])[0], results))

        obj = SimpleProfileSerializer(results, many=True).data

    elif type == 'tag_post':
        obj = Post_Tag.objects.filter(tag_id=int(query)).select_related('post_tag', 'post__project').order_by('-id')
        obj = Paginator(obj, 5)
        if obj.num_pages < page:
            return Response(status=status.HTTP_204_NO_CONTENT)

        obj = MainloadSerializer(obj.get_page(page), many=True).data
        for p in obj:
            if user_id == p['user_id']:
                p.update({"is_user":1})
            else:
                p.update({"is_user":0})
    
    elif type == 'company':
        obj = Company.objects.filter(company_name__icontains=query)
        obj = Paginator(obj, 20)
        if obj.num_pages < page:
            return Response(status=status.HTTP_204_NO_CONTENT)
        
        obj = SearchCompanySerializer(obj.get_page(page), many=True).data
    # if page == '1':
        # if 'tag' in type:
        #     interest_list = InterestTag.objects.get_or_create(user_id=request.user.id)[0]
        #     interest_list = interest_tag(interest_list, 'plus', int(query), 1)
        #     interest_list.save()
        # else:         
        #     Log.objects.create(user_id=request.user.id, query=query, type=type_int[type])

    
    return Response(obj, status=status.HTTP_200_OK)

@api_view(['GET', 'POST', 'DELETE'])
def search_log(request):
    user_id = request.user.id
    if request.method == 'POST':
        type = int(request.GET['type'])
        obj = Log.objects.filter(user_id=user_id, type=type, query=request.GET['query'], viewed=True).order_by('-id')[:20]
        if obj.exists():
            return Response(status=status.HTTP_200_OK)
        else:
            obj = Log.objects.create(user_id=user_id, type=type, query=request.GET['query'])
            return Response(LogSerializer(obj).data, status=status.HTTP_200_OK)
    
    elif request.method == 'GET':
        obj = Log.objects.filter(user_id=user_id, viewed=True).order_by('-id')[:20]
        return Response(LogSerializer(obj, many=True).data, status=status.HTTP_200_OK)
    
    elif request.method == 'DELETE':
        if request.GET['type'] == 'one':
            Log.objects.filter(id=request.GET['id']).update(viewed=False)
        elif request.GET['type'] == 'all':
            Log.objects.filter(user_id=user_id).update(viewed=False)
        return Response(status=status.HTTP_200_OK)
    
@api_view(['GET', ])
def search_university(request):
    if request.GET['type'] == 'school':
        try:
            obj = School.objects.filter(school__icontains=request.GET['query'])[:10]
            
            return Response(SchoolSerializer(obj, many=True).data, status=status.HTTP_200_OK)
        except:
            return Response(status=status.HTTP_204_NO_CONTENT)
    
    elif request.GET['type'] == 'department':
        try:
            obj = Department.objects.filter(school_id=request.GET['id'])
            obj = obj.filter(department__icontains=request.GET['query'])[:10]

            return Response(DepSerializer(obj, many=True).data, status=status.HTTP_200_OK)
        except:
            return Response(status=status.HTTP_204_NO_CONTENT)

@api_view(['GET'])
@permission_classes((IsAuthenticated,))
def recommend(request):
    now = datetime.datetime.now()
    post_obj = Post.objects.filter(date__range=[now-datetime.timedelta(days=7), now]).select_related('project').order_by('-like_count')
    post_obj = Paginator(post_obj, 5)
    if post_obj.num_pages < int(request.GET['page']):
        return Response(status=status.HTTP_204_NO_CONTENT)
    
    return Response(MainloadSerializer(post_obj.get_page(request.GET['page']), many=True).data, status=status.HTTP_200_OK)

@api_view(['GET'])
@permission_classes((IsAuthenticated,))
def search_company(request):
    try:
        company_obj = Company_Inform.objects.filter(company_name__icontains=request.GET['query']).order_by('-id')
        company_obj = Paginator(company_obj, 10)
        if company_obj.num_pages < int(request.GET['page']):
            return Response(status=status.HTTP_204_NO_CONTENT)

        return Response(SimpleComapnyProfileSerializer(company_obj.get_page(request.GET['page']), many=True).data, status=status.HTTP_200_OK)
    except:
        return Response(status=status.HTTP_204_NO_CONTENT)
