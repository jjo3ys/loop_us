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
from user_api.models import Banlist, Company, Profile, School, Department
from user_api.serializers import SchoolSerializer, DepSerializer, SimpleProfileSerializer, CompanySerializer
from tag.models import Post_Tag

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

@api_view(['GET', ])
@permission_classes((IsAuthenticated,))
def search(request, type):
    query = request.GET['query']
    page = request.GET['page']
    try:
        ban_list = Banlist.objects.filter(user_id=request.user.id)[0].banlist
    except:
        ban_list = []

    ban_list += Banlist.objects.filter(banlist__contains=request.user.id).values_list('user_id', flat=True)

    if type == 'post':
        obj = Post.objects.filter(contents__icontains=query).exclude(user_id__in=ban_list).order_by('-id')
        obj = Paginator(obj, 5)
        if obj.num_pages < int(page):
            return Response(status=status.HTTP_204_NO_CONTENT)

        obj = MainloadSerializer(obj.get_page(page), many=True).data
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
        page= int(page)
        results = es.search(index='profile', body={'query':{'match':{"text":{"query":query, "analyzer":"ngram_analyzer"}}}}, size=1000)['hits']['hits'][(page-1)*10:page*10]
        results = list(map(lambda x: Profile.objects.filter(user_id=x['_source']['user_id'])[0], results))
    
        obj = SimpleProfileSerializer(results, many=True).data

    elif type == 'tag_post':
        obj = Post_Tag.objects.filter(tag_id=int(query)).select_for_update('post_tag').order_by('-id')
        obj = Paginator(obj, 5)
        if obj.num_pages < int(page):
            return Response(status=status.HTTP_204_NO_CONTENT)

        obj = MainloadSerializer(obj.get_page(page), many=True).data
        for p in obj:
            if request.user.id == p['user_id']:
                p.update({"is_user":1})
            else:
                p.update({"is_user":0})

    elif type == 'notice':
        return Response("unrealized", status=status.HTTP_204_NO_CONTENT)
    
    # if page == '1':
        # if 'tag' in type:
        #     interest_list = InterestTag.objects.get_or_create(user_id=request.user.id)[0]
        #     interest_list = interest_tag(interest_list, 'plus', int(query), 1)
        #     interest_list.save()
        # else:         
        #     Log.objects.create(user_id=request.user.id, query=query, type=type_int[type])

    
    return Response(obj, status=status.HTTP_200_OK)

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
    post_obj = Post.objects.filter(date__range=[now-datetime.timedelta(days=7), now]).order_by('-like_count')
    post_obj = Paginator(post_obj, 5)
    if post_obj.num_pages < int(request.GET['page']):
        return Response(status=status.HTTP_204_NO_CONTENT)
    
    return Response(MainloadSerializer(post_obj.get_page(request.GET['page']), many=True).data, status=status.HTTP_200_OK)

@api_view(['GET'])
@permission_classes((IsAuthenticated,))
def search_company(request):
    try:
        company_obj = Company.objects.filter(company_name__icontains=request.GET['query']).order_by('-count')
        company_obj = Paginator(company_obj, 10)
        if company_obj.num_pages < int(request.GET['page']):
            return Response(status=status.HTTP_204_NO_CONTENT)

        return Response(CompanySerializer(company_obj.get_page(request.GET['page']), many=True).data, status=status.HTTP_200_OK)
    except:
        return Response(status=status.HTTP_204_NO_CONTENT)
