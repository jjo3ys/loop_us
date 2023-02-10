from django.core.paginator import Paginator

from rest_framework.response import Response
from rest_framework.decorators import APIView
from rest_framework import status

from django.db.models import F, Count

from config.settings import COUNT_PER_PAGE

from user.utils import PROFILE_SELECT_LIST
from user.models import Alarm, Banlist, Profile
from user.serializers import RankProfileListSerializer
from user.push_fcm import cocomment_fcm, cocomment_like_fcm, comment_fcm, comment_like_fcm, like_fcm, public_pj_fcm, tag_fcm

from .models import *
from .serializers import CareerListSerializer, CocommentListSerializer, CommentSerializer, MainPageSerializer, PostSerializer
from .utils import POST_PREFETCH_LIST, POST_SELECTE_LIST

from datetime import date

import datetime

# 커리어
class CareerAPI(APIView):
    # 커리어 작성
    def post(self, request):
        user = request.user
        data = request.data

        career_obj = Career.objects.create(
                        career_name = data["career_name"],
                        is_public   = data["is_public"]
                        )  

        # 기업 관련 커리어일 때
        if "company_id" in data:
            career_obj.tag_company = True
            career_obj.thumbnail   = data["company_id"]
            career_obj.save()
        
        career_obj = CareerUser.objects.create(user_id=user.id, career_id=career_obj.id)
        career_obj = CareerListSerializer(career_obj, read_only=True).data

        return Response(career_obj, status=status.HTTP_200_OK)
    
    # 커리어 불러오기
    def get(self, request):
        user  = request.user
        param = request.GET

        career_obj = CareerUser.objects.prefetch_related("career__post"
                        ).get(career_id=param["career_id"], user_id=param["user_id"])
        
        career_obj = CareerListSerializer(career_obj, read_only=True).data
        return Response(career_obj, status=status.HTTP_200_OK)

    # 커리어 수정
    def put(self, request):
        user  = request.user
        param = request.GET
        data  = request.data

        put_type = param["type"]

        career_obj = Career.objects.get(id=param["id"])
        
        # 커리어 이름 변경
        if put_type == "career_name":
            career_obj.career_name = data["career_name"]
        
        # 공용 커리어에 사용자 추가
        elif put_type == "looper":
            looper_list = data.getlist("looper")

            profile_obj = Profile.objects.get(user_id=user.id)
            
            for looper in looper_list:
                CareerUser.objects.create(career_id=career_obj.id, user_id=looper, is_manager=False)
                tag_fcm(looper, profile_obj.real_name, user.id, career_obj.career_name, career_obj.id)
        
        career_obj.save()
        career_obj = CareerUser.objects.select_related("career").get(career_id=param["id"], user_id=user.id)
        career_obj = CareerListSerializer(career_obj, read_only=True).data

        return Response(career_obj, status=status.HTTP_200_OK)
    
    # 커리어 삭제
    def delete(self, request):
        user  = request.user
        param = request.GET

        del_type = param["type"]

        if del_type == "exit":
            CareerUser.objects.get(career_id=param["id"], user_id=user.id).delete()
        
        elif del_type == "del":
            career_obj  = Career.objects.prefetch_related(
                            "post_contents_image", "post_contents_file"
                            ).get(id=param["id"])
            profile_obj = Profile.objects.get(id=user.id)

            file_size = 0
            post_list = career_obj.post.all()
            # 커리어내 포스트 이미지, 파일 삭제
            for post in post_list:
                for image in post.contents_image.all():
                    image.image.delete(save=False)
                
                for file in post.contents_file.all():
                    file_size += file.file.size
                    file.file.delete(save=False)
            
            profile_obj.upload_size = max(profile_obj.upload_size-file_size, 0)
            profile_obj.save()

            Alarm.objects.filter(type=3, target_id=param["id"]).delete()

            post_list = post_list.values_list("id", flat=True)
            Alarm.objects.filter(target_id__in=post_list, type__in=[i for i in range(4, 9)]).delete()
            career_obj.delete()
        
        return Response(status=status.HTTP_200_OK)

# 포스트
class PostAPI(APIView):
    def post(self, request):
        user  = request.user
        data  = request.data
        param = request.GET

        tags   = data.getlist("tag")
        files  = data.getlist("file")
        links  = data.getlist("link")
        images = data.getlist("image")

        # 인당 업로드 용량 제한 (30mb 까지)
        file_size = sum(list(map(lambda x:x.size, files)))
        profile_obj = user.profile
        profile_obj.upload_size += file_size
        
        if profile_obj.upload_size > 31_457_280: return Response(status=status.HTTP_406_NOT_ACCEPTABLE)

        profile_obj.save()        

        post_obj = Post.objects.create(
                    user_id   = user.id,
                    career_id = param["id"],
                    contents  = data["contents"]
                    )
        
        # 포스트 이미지, 파일 
        images = [PostImage(post_id=post_obj.id, image=image) for image in images]
        links  = [PostLink(post_id=post_obj.id, link=link) for link in links]

        PostImage.objects.bulk_create(images)
        PostLink.objects.bulk_create(links)

        # 포스트 태그
        for tag in tags:
            tag_obj, created = Tag.objects.get_or_create(tag=tag)
            Post_Tag.objects.create(post_id=post_obj.id, tag_id=tag_obj.id)
            if not created:
                tag_obj.count += 1
                tag_obj.save()

        # 커리어의 최근 포스트 업로드 시간 업데이트
        post_obj.career.post_update_date = datetime.datetime.now()
        
        # 커리어의 썸네일 업데이트
        if  not post_obj.career.tag_company and images:
            post_obj.career.thumbnail = PostImage.objects.filter(post_id=post_obj.id).first().id
       
        # 커리어의 포스트 개수 업데이트
        CareerUser.objects.filter(user_id=user.id, career_id=param["id"]
            ).update(post_count=F("post_count") + 1)

        # 공유 커리어일 때 팀원에게 알람
        if post_obj.career.is_public:
            public_pj_fcm(post_obj.career_id, post_obj.id, user.id, post_obj.career.career_name)
        
        post_obj = PostSerializer(post_obj, read_only=True, context={"user_id":user.id}).data
        return Response(post_obj, status=status.HTTP_200_OK)

    def get(self, request):
        user  = request.user
        param = request.GET

        post_obj = Post.objects.select_related(
                    POST_SELECTE_LIST
                    ).prefetch_related(
                        POST_PREFETCH_LIST + ["comments__user__profile__" + _ for _ in PROFILE_SELECT_LIST ]
                    ).get(id=param["id"])
        post_obj.view_count += 1
        post_obj.save()
        post_obj = PostSerializer(post_obj, read_only=True, context={"user_id":user.id}).data
        return Response(post_obj, status=status.HTTP_200_OK)

    def put(self, request):
        data  = request.data
        param = request.GET

        post_obj = Post.objects.select_related("career").get(id=param["id"])
        post_obj.contents = data["contents"]

        tag_obj  = Post_Tag.objects.filter(post_id=post_obj.id).select_related("tag")
        
        origin_tag = tag_obj.values_list("tag__tag", flat=True)
        new_tag    = data.getlist("tag")
        
        del_tag = [tag for tag in origin_tag if tag not in new_tag]
        add_tag = [tag for tag in new_tag if tag not in origin_tag]

        Tag.objects.filter(tag__in=del_tag).update(count=F("count")-1)
        tag_obj.delete()

        for tag in add_tag:
            tag, created = Tag.objects.get_or_create(tag=tag)
            Post_Tag.objects.create(tag=tag, post_id=post_obj.id)

            if not created:
                tag_obj.count += 1
                tag_obj.save()

        post_obj.save()
        return Response(status=status.HTTP_200_OK)
    
    def delete(self, request):
        user  = request.user
        param = request.GET

        post_obj = Post.objects.select_related(
                    "career").prefetch_related(
                        "contents_image", "contents_file", "post_tag"
                    ).get(id=param["id"])
        career_id = post_obj.career_id

        tag_list = post_obj.post_tag.all().values_list("tag_id")
        Tag.objects.filter(id__in=tag_list).update(count=F("count")-1)

        for image in post_obj.contents_image.all():
            image.image.delete(save=False)

        # 업로드 크기 총합 업데이트
        file_size = 0
        for file in  post_obj.contents_file.all():
            file_size += file.file.size()
            file.file.delete(save=False)
        
        profile_obj = Profile.objects.get(user_id=user.id)
        profile_obj.upload_size = max(profile_obj.upload_size-file_size, 0)
        profile_obj.save()

        # 내 커리어에서 포스트 수 -1
        CareerUser.objects.filter(user_id=user.id, career_id=career_id).update(post_count=F("post_count")-1)
        # 포스트 관련 알람 삭제
        Alarm.objects.filter(type__in=[i for i in range(4, 10)], target_id=param["id"]).delete()
        post_obj.delete()

        if not post_obj.career.tag_company:
            career_obj = Career.objects.prefetch_related("post__contents_image").get(id=career_id)
            # 커리어 내 이미지가 있는 다른 포스팅
            img_obj = career_obj.post.annotate(
                         img_count=Count("contents_image")
                      ).filter(img_count__gte=1).order_by("-id", "-contents_image")

            if img_obj.exist(): thumb_id = img_obj.first().contents_image.id
            else: thumb_id = 0
            career_obj.thumbnail = thumb_id
        
        return Response(status=status.HTTP_200_OK)
        
# 댓글, 대댓글
class CommentAPI(APIView):
    def post(self, request):
        user  = request.user
        data  = request.data
        param = request.GET

        post_type = param["type"]
        # 댓글 작성
        if post_type == "comment":
            comment_obj = Comment.objects.create(
                            user_id = user.id,
                            post_id = param["id"],
                            content = data["content"]
                         )
            # 포스트 작성자가 아닐 때 알람
            if comment_obj.post.user_id != user.id:
                profile_obj = user.profile
                comment_fcm(comment_obj.post.user_id, profile_obj.real_name, param["id"], user.id)
            
        # 대댓글 작성
        else:
            comment_obj = Cocomment.objects.create(
                            user_id    = user.id,
                            comment_id = param["id"],
                            content    = data["content"],
                            tagged_id  = data["tagged_user"]
                          )
            # 댓글 작성자가 아닐 때 알람
            if user.id != comment_obj.user.id:
                profile_obj = user.profile
                cocomment_fcm(data["tagged_user"], profile_obj.real_name, comment_obj.id, user.id, comment_obj.comment.post_id)
        
        return Response(status=status.HTTP_200_OK)

    # 댓글 리스트
    def get(self, request):
        param = request.GET

        get_type = param["type"]
        
        if get_type == "comment":
            comment_obj = Comment.objects.select_related(
                            ["user__profile"+_ for _ in PROFILE_SELECT_LIST]).filter(post_id=param["id"], id__lt=param["last"]).order_by("-id")[:COUNT_PER_PAGE]
            comment_obj = CommentSerializer(comment_obj, many=True, read_only=True).data
        else: 
            comment_obj = Cocomment.objects.select_related(
                            ["user__profile"+_ for _ in PROFILE_SELECT_LIST]).filter(comment_id=param["id"], id__lt=param["last"]).order_by("-id")[:COUNT_PER_PAGE]
            comment_obj = CocommentListSerializer(comment_obj, many=True, read_only=True).data
        
        return Response(comment_obj, status=status.HTTP_200_OK)
    
    # 댓글 수정
    def put(self, request):
        data  = request.data
        param = request.GET

        put_type = param["type"]

        if put_type == "comment":
            comment_obj = Comment.objects.get(id=param["id"])
        else:
            comment_obj = Cocomment.objects.get(id=param["id"])

        comment_obj.content = data["content"]
        comment_obj.save()
        
        return Response(status=status.HTTP_200_OK)
    
    # 댓글 삭제
    def delete(self, request):
        param = request.GET

        del_type = param["type"]

        if del_type == "comment":
            comment_obj = Comment.objects.get(id=param["id"])
            # 댓글 관련 알람 삭제
            Alarm.objects.filter(type__in=[5, 7], target_id=comment_obj.post_id).delete()
        else:
            comment_obj = Cocomment.objects.get(id=param["id"])
            # 대댓글 관련 알람 삭제
            Alarm.objects.filter(type__in=[6, 8], target_id=comment_obj.comment.post).delete()
        
        comment_obj.delete()
        
        return Response(status=status.HTTP_200_OK)

# 좋아요(포스트, 댓글, 대댓글)
class LikeAPI(APIView):
    def update_count(self, obj, count):
        obj.like_count += count
        obj.save()

    def send_alarm(self, obj, real_name, like_id, post_id, func, user):
        if obj.user_id != user.id:
            param = {
                "topic": obj.user_id,
                "req_from":real_name,
                "id": like_id,
                "from_id":user.id,
                "post_id":post_id
            }
            func(param)
    # 좋아요
    def post(self, request):
        user  = request.user
        param = request.GET

        post_type = param["type"]

        if post_type == "post":
            like_obj = Like.objects.create(post_id=param["id"], user_id=user.id)
            
            obj       = like_obj.post
            post_id   = None
            send_func = like_fcm
        
        elif post_type == "comment":
            like_obj = CommentLike.objects.create(comment_id=param["id"], user_id=user.id)
            
            obj       = like_obj.comment
            post_id   = like_obj.comment.post_id
            send_func = comment_like_fcm
            
        else:
            like_obj = CocommentLike.objects.create(cocomment_id=param["id"], user_id=user.id)
            
            obj       = like_obj.cocomment
            post_id   = like_obj.cocomment.comment.post_id
            send_func = cocomment_like_fcm

        self.send_alarm(obj, user.profile.real_name, param["id"], post_id, send_func, user) 
        self.update_count(obj, 1)     

        return Response(status=status.HTTP_200_OK)  
    
    # 좋아요 취소
    def delete(self, request):
        user  = request.user
        param = request.GET

        del_type = param["type"]

        if del_type == "post":
            obj = Like.objects.get(post_id=param["id"], user_id=user.id)
        elif del_type == "comment":
            obj = CommentLike.objects.get(comment_id=param["id"], user_id=user.id)
        else:
            obj = CocommentLike.objects.get(cocomment_id=param["id"], user_id=user.id)
        
        self.update_count(obj, -1)

        return Response(status=status.HTTP_200_OK)
    
    # 좋아요 리스트
    def get(self, request):
        param = request.GET
        
        get_type  = param["type"]

        if get_type == "post":
            like_obj = Like.objects.select_related(["user__profile__"+ _ for _ in PROFILE_SELECT_LIST]).filter(post_id=param["id"])
        elif get_type == "comment":
            like_obj = CommentLike.objects.select_related(["user__profile__"+ _ for _ in PROFILE_SELECT_LIST]).filter(comment_id=param["id"])
        else:
            like_obj = CocommentLike.objects.select_related(["user__profile__"+ _ for _ in PROFILE_SELECT_LIST]).filter(cocomment_id=param["id"])
        
        like_obj = list(map(lambda x: x.user.profile, like_obj))
        like_obj = RankProfileListSerializer(like_obj, many=True, read_only=True).data

        return Response(like_obj, status=status.HTTP_200_OK)

# 북마크
class BookMarkAPI(APIView):
    # 북마크
    def post(self, request):
        user  = request.user
        param = request.GET

        BookMark.objects.create(post_id=param["id"], user_id=user.id)

        return Response(status=status.HTTP_200_OK)
    
    # 북마크 삭제
    def delete(self, request):
        user  = request.user
        param = request.GET

        BookMark.objects.get(post_id=param["id"], user_id=user.id).delete()

        return Response(status=status.HTTP_200_OK)
    
    # 북마크 리스트
    def get(self, request):
        user  = request.user
        param = request.GET

        page = param["page"]

        post_obj = BookMark.objects.filter(user_id=user.id)
        post_obj = post_obj[(page-1)*COUNT_PER_PAGE:page*COUNT_PER_PAGE]
        post_obj = post_obj.select_related(["post__"+_ for _ in POST_SELECTE_LIST]
                    ).prefetch_related(["post__"+_ for _ in POST_PREFETCH_LIST])
        post_obj = list(map(lambda x:x.post, post_obj))    

        like_list = dict(Like.objects.filter(user_id=user.id, post__in=post_obj).values_list("post_id", "user_id"))
        post_obj = MainPageSerializer(post_obj, many=True, read_only=True, context={"like_list":like_list}).data

        return Response(post_obj, status=status.HTTP_200_OK)

# 메인 페이지 포스트 리스트
class MainPageAPI(APIView):
    def get(self, request):
        user  = request.user
        param = request.GET

        last = int(param["last"])
        # 내가 밴한, 밴 당한 리스트

        ban_list = Banlist.objects.get(user_id=user.id).banlist
        ban_list += Banlist.objects.filter(banlist__contains=user.id).values_list("user_id", flat=True)

        post_obj = Post.objects.all(
                    ).select_related(POST_PREFETCH_LIST
                    ).prefetch_related(POST_PREFETCH_LIST).exclude(user_id__in=ban_list).order_by("-id")
        
        if last: post_obj = post_obj.filter(id__lt=last)

        post_obj  = list(post_obj[:COUNT_PER_PAGE])
        like_list = dict(Like.objects.filter(user_id=user.id, post__in=post_obj).values_list("post_id", "user_id"))
        book_list = dict(BookMark.objects.filter(user_id=user.id, post__in=post_obj).values_list("post_id", "user_id"))
        post_obj  = MainPageSerializer(post_obj, many=True, read_only=True, context={"user_id":user.id, "like_list":like_list, "book_list":book_list})

        return Response(post_obj, status=status.HTTP_200_OK)

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