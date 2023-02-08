from django.core.paginator import Paginator

from rest_framework.response import Response
from rest_framework.decorators import APIView
from rest_framework import status


from config.settings import COUNT_PER_PAGE

from .models import *
from .serializers import MainPageSerializer

from datetime import date

# 해당 태그를 사용한 최신 & 인기 게시물들
class TagPost(APIView):
    # post_tag object에서 post만 분리하여 사용
    def get_post_obj(self, post_obj, user, count_per_page=COUNT_PER_PAGE, page=0):
        post_obj = post_obj[(page-1)*count_per_page : page*count_per_page]

        post_obj = post_obj.prefetch_related(
            "post__contents_image", "post__contents_link", "post__contents_file",
            "post__comments__cocomments", "post__post_like", "post__post_tag")

        post_obj = list(map(lambda x: x.post, post_obj))
        
        like_list = dict(Like.objects.filter(user_id=user.id, post__in=post_obj).values_list("post_id", "user_id"))
        book_list = dict(BookMark.objects.filter(user_id=user.id, post_id__in=post_obj).values_list("post_id", "user_id"))
        
        return MainPageSerializer(post_obj, many=True, read_only=True, context={"like_list":like_list, "book_list":book_list, "user_id":user.id}).data

    def get(self, request):
        user  = request.user
        param = request.GET

        page      = int(param["page"])
        target_id = param["id"]

        post_obj = Post_Tag.objects.filter(tag_id=target_id).select_related("post__career")
        # 첫페이지에서 최신, 인기, 태그 사용 동향
        if page == 1:
            # 지난 6개월간 태그 사용 동향
            lastmonth = date.today().month - 1
            tag_obj = Tag.objects.get(id=target_id)
            count = {}
            for i in range(7):
                if lastmonth - i <= 0: month = str(12 + lastmonth - i)
                else: month = str(lastmonth - i)

                if month in tag_obj.monthly_count: count[month] = tag_obj.monthly_count[month]
                else: count[month] = 0

            # 최신 포스트
            new_post_obj = post_obj.order_by("-id")
            new_post_obj = self.get_post_obj(new_post_obj, user, count_per_page=int(COUNT_PER_PAGE/2))

            # 인기 포스트
            pop_post_obj = post_obj.order_by("-post__like_count")
            pop_post_obj = self.get_post_obj(pop_post_obj, user, count_per_page=int(COUNT_PER_PAGE/2))
            
            return Response({"monthly_count":count, "related_new":new_post_obj, "related_pop":pop_post_obj}, status=status.HTTP_200_OK)
        
        elif page > post_obj.count()//COUNT_PER_PAGE+1: return Response(status=status.HTTP_204_NO_CONTENT)

        # 2페이지 이상 인기, 최신 포스팅 분류
        if param["type"] == "new": post_obj = post_obj.order_by("-id")
        else: post_obj = post_obj.order_by("post__like_count")

        post_obj = self.get_post_obj(post_obj, user, page=page)

        return Response(post_obj, status=status.HTTP_200_OK)