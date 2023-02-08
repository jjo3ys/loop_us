from django.core.paginator import Paginator

from rest_framework.response import Response
from rest_framework.decorators import APIView
from rest_framework import status

from config.settings import COUNT_PER_PAGE

from career.models import BookMark, Like, Post, Post_Tag
from career.serializers import MainPageSerializer

from user.utils import ES
from user.models import Banlist, Company, Company_Inform, Department, Profile, School
from user.serializers import DepSerializer, ProfileListSerializer, SearchCompanySerializer, SchoolSerializer

from .models import Log
from .serializers import LogSerializer, CompanyProfileListSerializer

class Search(APIView):
    def get(self, request):
        user  = request.user
        param = request.GET

        page        = int(param["page"])
        query       = param["query"]
        search_type = param["type"]

        # 밴 리스트
        try: ban_list = Banlist.objects.get(user_id=user.id).banlist
        except: ban_list = []
        ban_list += Banlist.objects.filter(ban_list__contains=user.id).values_list("user_id", flat=True)

        # 포스팅 검색
        if search_type == "post":
            obj = Post.objects.filter(contents__icontains=query
                  ).exclude(user_id__in=ban_list
                  ).select_related(
                    "career").prefetch_related(
                    "user__profile__department", "user__profiel__school",
                    "comments__cocomments",
                    "contents_image", "contents_link", "contents_file", "post_like", "post_tag", "bookmark"
                    ).order_by("-id")
            if obj.count()//COUNT_PER_PAGE+1 < page: return Response(status=status.HTTP_204_NO_CONTENT)

            obj = obj[(page-1)*COUNT_PER_PAGE:page*COUNT_PER_PAGE]
            post_list = list(obj)
            like_list = dict(Like.objects.filter(user_id=user.id, post_in=post_list).values_list("post_id", "user_id"))
            book_list = dict(BookMark.objects.filter(user_id=user.id, post__in=post_list).values_list("post_id", "user_id"))
            obj = MainPageSerializer(obj, many=True, context={"user_id":user.id, "like_list":like_list, "book_list":book_list}).data

        # 프로필 검색
        elif search_type == "profile":
            results = ES.search(index="profile", body={"query":{"match":{"text":{"query":query, "analyzer":"ngram_analyzer"}}}},
                                size=1000)["hits"]["hits"][(page-1)*COUNT_PER_PAGE:page*COUNT_PER_PAGE]
            
            if len(results) == 0: return Response(status=status.HTTP_204_NO_CONTENT)     
            results = list(map(lambda x: Profile.objects.get(user_id = x["_source"]["user_id"]), results))
            obj = ProfileListSerializer(results, many=True, read_only=True).data
        
        # 같은 태그를 사용한 포스팅 검색
        elif search_type == "tag_post":
            obj = Post_Tag.objects.filter(tag_id=int(query)
                  ).select_related("post__career"
                  ).prefetch_related(
                    "post__contents_image", "post__contents_link", "post__contents_file", "post__post_like", "post__post_tag",
                    "post__comments__cocomments"
                  ).order_by('-id')

            if obj.count()//COUNT_PER_PAGE+1 < page: return Response(status=status.HTTP_204_NO_CONTENT)

            obj = obj[(page-1)*COUNT_PER_PAGE:page*COUNT_PER_PAGE]
            post_list = list(obj.values_list("post_id", flat=True))
            like_list = dict(Like.objects.filter(user_id=user.id, post__in=post_list).values_list("post_id", "user_id"))
            book_list = dict(BookMark.objects.filter(user_id=user.id, post__in=post_list).values_list("post_id", "user_id"))
            obj = MainPageSerializer(obj, many=True, context={"user_id":user.id, "like_list":like_list, "book_list":book_list})

        # 회사 프로필 검색
        elif search_type == "company":
            obj = Company.objects.filter(company_name__icontains=query)
            obj = Paginator(obj, COUNT_PER_PAGE)
            if obj.num_pages < page: return Response(status=status.HTTP_204_NO_CONTENT)

            obj = SearchCompanySerializer(obj.get_page(page), many=True).data
    
        return Response(obj, status=status.HTTP_200_OK)

# 검색 기록 리스트
class SearchLog(APIView):
    # 검색 기록 남김
    def post(self, request):
        user  = request.user
        param = request.GET

        obj = Log.objects.filter(user_id=user.id, type=param["type"], query=param["query"], viewd=True
              ).order_by('-id')[:COUNT_PER_PAGE]
        # 최근 기록 20개 이내에 검색한 적 있음
        if obj.exists(): return Response(status=status.HTTP_200_OK)
        
        obj = Log.objects.create(user_id=user.id, type=param["type"], query=param["query"])
        return Response(LogSerializer(obj, read_only=True).data, status=status.HTTP_200_OK)
    
    def get(self, request):
        user  = request.user
        param = request.GET

        obj = Log.objects.filter(user_id=user.id ,viewd=True
              ).order_by("-id")[:COUNT_PER_PAGE]
        return Response(LogSerializer(obj, many=True, read_only=True).data, status=status.HTTP_200_OK)

    def delete(self, request):
        user  = request.user
        param = request.GET

        del_type = param["type"]

        # 특정 검색 기록 삭제
        if del_type == "one":
            Log.objects.filter(id=param["id"]).update(viewd=False)
        # 모든 검색 기록 삭제
        else:
            Log.objects.filter(user_id=user.id).update(viewd=False)
        return Response(status=status.HTTP_200_OK)

# 학교, 학과 검색
class SearchUniversity(APIView):
    def get(self, request):
        param = request.GET
        
        query       = param["query"]
        search_type = param["type"]

        if search_type == "school":
            obj = School.objects.filter(school__icontains=query)
            if obj:
                return Response(SchoolSerializer(obj[:10], many=True, read_only=True).data, status=status.HTTP_200_OK)
        elif search_type == "department":
            school_id = param["id"]
            obj = Department.objects.filter(school_id=school_id, department__icontains=query)
            if obj:
                return Response(DepSerializer(obj[:10], many=True, read_only=True).data, status=status.HTTP_200_OK)
        
        return Response(status=status.HTTP_204_NO_CONTENT)

# 회사 검색
class SearchCompany(APIView):
    def get(self, request):
        param = request.GET

        query = param["query"]
        page  = int(param["page"])

        company_obj = Company_Inform.objects.filter(company_name__icontains=query).order_by("-id")
        company_obj = Paginator(company_obj, COUNT_PER_PAGE)

        if company_obj.num_pages < page: return Response(status=status.HTTP_204_NO_CONTENT)

        return Response(CompanyProfileListSerializer(company_obj.get_page(page), many=True, read_only=True).data, status=status.HTTP_200_OK)
