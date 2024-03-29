from django.contrib.auth import authenticate
from django.contrib.auth.models import User
from django.contrib.auth.hashers import check_password
from django.core.mail import EmailMessage
from django.db.models import Sum, F, Count, SmallIntegerField, ExpressionWrapper
from django.utils import timezone

from rest_framework.response import Response
from rest_framework.decorators import APIView
from rest_framework.authtoken.models import Token
from rest_framework import status

from .utils import ES, CLIENT, PROFILE_SELECT_LIST, send_msg, email_format
from .push_fcm import loop_fcm, rank_fcm, report_alarm
from .models import *
from .serializers import *

from career.utils import delete_tag, POST_PREFETCH_LIST, POST_SELECTE_LIST
from career.models import *
from career.serializers import CareerListSerializer, MainPageSerializer

from config.settings import COUNT_PER_PAGE

from dateutil.relativedelta import relativedelta

import datetime

# 인증번호 확인
class Activate(APIView):
    def post(self, request):
        data        = request.data
        user_obj    = User.objects.filter(username=email)
        
        email       = data["eamil"]
        certify_num = data["certify_num"]
        
        num         = CLIENT.get(email.replace("@", ""))
        num         = str(num, "utf-8")
        
        if num == certify_num:
            CLIENT.delete(email)
            if user_obj.exists(): # 비밀번호 바꾸기
                user_obj.update(is_active=True)
            return Response(status=status.HTTP_200_OK)
        
        return Response(status=status.HTTP_401_UNAUTHORIZED)            # 인증번호 맞지 않음

# 인증번호 전송
class Certification(APIView):
    def post(self, request):
        param     = request.GET
        data      = request.data
        
        is_create = int(param["is_create"])
        email     = data["email"]
        user_obj  = User.objects.filter(username=email)
        
        if is_create and user_obj.exists():                             # 해당 이메일로 가입되어 있는 유저가 존재
            return Response(status=status.HTTP_400_BAD_REQUEST)
        else:
            send_msg(email)
            return Response(status=status.HTTP_200_OK)

# 인증 완료 후 회원가입 
class Signup(APIView):
    def post(self, request):
        data      = request.data
        
        user_obj = User.objects.create_user(
            username = data["email"],
            email    = data["email"],
            password = data["password"]
        )
        token_obj = Token.objects.create(
            user=user_obj
        )
        try:
            profile_obj = Profile.objects.create(
                user          = user_obj,
                real_name     = data["real_name"],
                department_id = data["department"],
                school_id     = data["school"],
                admission     = data["admission"],
                type          = data["type"]
            )
        except: # 프로필 양식에 알맞지 않아 생성이 안됨
            token_obj.delete()
            user_obj.delete()
            return Response(status=status.HTTP_404_NOT_FOUND)
        
        
        if profile_obj.department:                              
            text = profile_obj.school.school + " " + profile_obj.department.department + " " + profile_obj.real_name    # 학생 계정 + 학과 계정
        else:                                                     
            text = profile_obj.school.school + " " + profile_obj.real_name                                              # 학교 계정
            
        body = {
                "user_id":user_obj.id,
                "text":text
            }
        ES.index(index="profile", doc_type="_doc", body=body)
        
        # 일반 사용자일 떄 시작 커리어 생성
        if not int(data["type"]):                                                                                               # 학생 계정일 때만 기본 커리어 생성
            career_obj = Career.objects.create(
                career_name = "나만의 커리어",
                is_public   = False
            )
            CareerUser.objects.create(
                user   = user_obj,
                career = career_obj
            )
        
        return_data = {
            "token"        : token_obj.key,
            "school_id"    : "school"+str(data["school"]),
            "department_id": "department"+str(data["department"]),
            "is_student"   : 1,
            "user_id"      : str(user_obj.id)
        }
              
        return Response(data=return_data, status=status.HTTP_201_CREATED)

# 회원 탈퇴
class Resign(APIView):
    def post(self, request):
        user_obj = request.user
        data     = request.data
        
        reason   = data["reason"]
        
        profile_obj = Profile.objects.select_related("department", "school").get(user_id = user_obj.id)
        profile_obj.profile_image.delete(save=False)
        
        # 탈퇴 사유
        message = EmailMessage(
            subject = f"{profile_obj.real_name}님 탈퇴 사유",
            body    = f"{profile_obj.school.school} {profile_obj.department.department} \n 사유 : {reason}",
            to      = ["loopus@loopus.co.kr"]
        )
        
        try:
            message.send()
        except: return Response(status=status.HTTP_406_NOT_ACCEPTABLE)
        
        # 탈퇴 시 커리어 삭제 및 공유커리어에서 thumbnail 변경
        ## s3에서 업로드한 이미지, 파일 삭제
        careerUser_obj = CareerUser.objects.filter(user_id=user_obj.id)
        career_list = list(careerUser_obj.values_list("career_id", flat=True))
        career_dict = dict(Career.objects.filter(
            id__in=career_list, 
            is_public=True, 
            tag_company=False).exclude(thumnail=None).values_list("thumbnail", flat=True))
        
        post_obj = Post.objects.filter(user_id=user_obj.id).prefetch_related("contents_image", "contents_file")
        for post in post_obj:
            # 커리어 thumbnail 변경
            for image in post.contents_image.all():
                if image.id in career_dict:
                    post.career.thumbnail = None
                    post_list = Post.objects.filter(career_id=post.career_id).exclude(id=post.id)
                    post_image_obj = PostImage.objects.filter(post__in=post_list)             
                    if post_image_obj.exists():
                        post.career.thumbnail = post_image_obj.last().id               
                    post.career.save()
                image.image.delete(save=False)

            # 커리어 내 포스팅에 업로드 파일 삭제
            for file in post.contents_file.all():
                file.file.delete(save=False)

        # 자신이 방장인 커리어 삭제
        career_list = list(careerUser_obj.filter(is_manager=1).values_list("career_id", flat=True))
        Career.objects.filter(id__in=career_list).delete()
        
        # 사용자가 사용한 태그에서 count 변화
        tag_obj = Post_Tag.objects.filter(post___in=post_obj)
        delete_tag(tag_obj)
        
        #elasticsearch 서버에서 해당 사용자 삭제
        ES.delete_by_query(index="profile", doc_type="_doc", body={"query":{"match":{"user_id":{"query":request.user.id}}}})
        user = User.objects.filter(id=user_obj.id)
        user.delete()
        
        return Response(status=status.HTTP_200_OK)

#로그인   
class Login(APIView):
    def post(self, request):
        data     = request.data
        
        username = data["username"]
        password = data["password"]
        
        user_obj = authenticate(
            username = username,
            password = password
        )
        
        #로그인 정보가 존재하며, 활성화 상태
        if user_obj and user_obj.is_active:
            token_obj = Token.objects.get(user_id = user_obj.id)
            
            # 사용자 최근 로그인 시간 업데이트
            user_obj.last_login = timezone.now()
            user_obj.save()

            # 학생 사용자일 때
            profile_obj = Profile.objects.filter(user_id = user_obj.id)
            if profile_obj.exists():
                profile_obj = profile_obj.first()
                topic_list = list(CareerUser.objects.select_related("career")
                                  .filter(user_id=user_obj.id, career__is_public=True)
                                  .values_list("career_id", flat=True))
                return Response(data={
                    "token"        : token_obj.key,
                    "school_id"    : "school" + str(profile_obj.school_id),
                    "department_id": "department" + str(profile_obj.department_id),
                    "topic_list"   : topic_list,
                    "user_id"      : str(user_obj.id),
                    "is_student"   : 1
                }, status=status.HTTP_202_ACCEPTED)
            # 기업 사용자일 때
            else:
                return Response(data={
                    "token"     : token_obj.key,
                    "user_id"   : str(user_obj.id),
                    "is_student": 0
                })

#비밀번호 관련               
class Password(APIView):
    def put(self, request):
        user  = request.user
        param = request.GET
        data  = request.data
        
        put_type  = param["type"]
        
        #비밀번호 변경
        if put_type == "change" and check_password(data["origin_pw"], user.password):
            user.set_password(data["origin_pw"])
            user.save()
            return Response(status=status.HTTP_200_OK)
        
        # 인증 완료 후 비밀번호 설정
        elif put_type == "find":                                                      
            try: user = User.objects.get(email=data["email"])
            except: return Response(status=status.HTTP_401_UNAUTHORIZED)
            
            user.set_password(data["password"])
            user.save()
            return Response(status=status.HTTP_200_OK)
        return Response(status=status.HTTP_401_UNAUTHORIZED)
    
    # 비밀번호 찾기 인증과정
    def post(self, request):                                                      
        data  = request.data     
         
        email = data["email"]
        
        try: user = User.objects.get(email=email)
        except: return Response(status=status.HTTP_401_UNAUTHORIZED)
        user.is_active = False
        user.save()
        return Response(status=status.HTTP_200_OK)
    
# 문의
class Ask(APIView):
    def post(self, request):
        param     = request.GET
        data      = request.data
        
        ask_type      = param["type"]
        
        message = email_format(ask_type, data)

        try:
            message.send()
        except: return Response(status=status.HTTP_406_NOT_ACCEPTABLE)
        return Response(status=status.HTTP_200_OK)

# 기업 사용자 프로필
class CompanyProfile(APIView):
    def get(self, request):
        user  = request.user
        param = request.GET

        company_id = param["id"]
        is_student = param["is_student"]

        company_obj = Company_Inform.objects.select_related("company_logo").prefetch_related("inform_image").get(
            user_id = company_id
        )
        # 학생 사용자일 경우
        if int(is_student):
            company_obj.view_count += 1
            company_obj.save()

            # 탐색 기록 남김
            viewd, created = ViewCompany.objects.get_or_create(student_id = user.id, comapny_id = company_id)
            if not created:
                viewd.date = datetime.datetime.now()
                viewd.save()

        company_obj = CompanyProfileSerializer(company_obj, context={"user_id":user.id}).data

        return Response(company_obj, status=status.HTTP_200_OK)

# 학생 사용자 프로필
class StudentProfile(APIView):
    def get(self, request):
        user  = request.user
        param = request.GET

        target_id = param["id"]

        try: 
            profile_obj = Profile.objects.select_related(PROFILE_SELECT_LIST).prefetch_related("user_sns").get(
                user_id = target_id
            )
        except Profile.DoesNotExist: return Response(status=status.HTTP_404_NOT_FOUND)

        if user.id != int(target_id):
            is_banned = Banlist.objects.filter(user_id = target_id, banlist__contains=user.id).exists()
            # 프로필 주인이 나를 밴했을 때
            if is_banned: return Response(status=status.HTTP_204_NO_CONTENT)

            # 프로필 조회수 +1
            profile_obj.view_count += 1
            profile_obj.save()

  
        profile_obj = ProfileSerializer(profile_obj, context={"user_id":user.id}).data
       
        return Response(profile_obj, status=status.HTTP_200_OK)
    
    def put(self, request):
        user  = request.user
        data  = request.data
        param = request.GET
        files = request.FILES

        put_type    = param["type"]
        profile_obj = Profile.objects.select_related("department", "school").get(user_id = user.id)

        # 프로필 이미지 수정
        if put_type == "image":
            profile_obj.profile_image.delete(save=False)
            profile_obj.profile_image = files.get("image")
        
        # 프로필 수정(인증 필요)
        elif put_type == "profile":
            # 이메일 변경으로 인한 회원가입 아이디 변경
            user_obj = User.objects.get(user_id = user.id)

            user_obj.username = data["email"]
            user_obj.email    = data["email"]
            user_obj.save()

            profile_obj.real_name     = data["real_name"]
            profile_obj.school_id     = data["school"]
            profile_obj.department_id = data["department"]
            profile_obj.admission     = data["admission"]


            # 랭킹 초기화
            profile_obj.rank, profile_obj.last_rank, profile_obj.school_rank, profile_obj.school_last_rank = 0, 0, 0, 0

            # elasticsearch 색인 수정
            ES.delete_by_query(index="profile", doc_type="_doc", body={"query":{"match":{"user_id":{"query":request.user.id,}}}})
            body = {
                "user_id":request.user.id,
                "text":profile_obj.school.school + " " + profile_obj.department.department + " " + profile_obj.real_name
            }
            ES.index(index="profile", doc_type="_doc", body=body)
        
        # 프로필 sns url 수정
        elif put_type == "sns":
            sns_type = data["sns_type"]
            url      = data["url"]
            
            sns_obj, _  = UserSNS.objects.get_or_create(profile_id = profile_obj.id, type = sns_type)
            sns_obj.url = url
            sns_obj.save()
        
        profile_obj.save()

        return Response(status=status.HTTP_200_OK)
    
    def delete(self, request):
        param = request.GET
        user  = request.user

        del_type = param["type"]

        # 프로필 sns url 삭제
        if del_type == "sns":
            sns_id = param["id"]
            UserSNS.objects.get(id = sns_id).delete()
        
        # 프로필 이미지 삭제
        elif del_type == "image":
            profile_obj = Profile.objects.get(user_id = user.id)
            profile_obj.profile_image.delete(save = False)
            profile_obj.save()

        return Response(status=status.HTTP_200_OK)

# 프로필내 커리어
class ProfileCareer(APIView):
    # 커리어 리스트
    def get(self, request):
        param = request.GET

        target_id = param["id"]
        try:
            career_obj = CareerUser.objects.filter(user_id = target_id).select_related("career").order_by("order")
        except: return Response(status=status.HTTP_404_NOT_FOUND)
        career_obj = CareerListSerializer(career_obj, many=True).data
        return Response(career_obj, status=status.HTTP_200_OK)

    # 커리어 순서 변경
    def put(self, request):
        user = request.user
        data = request.data

        career_obj = CareerUser.objects.filter(user_id = user.id)
        for career in career_obj:
            career.order = data[str(career.career_id)]

        CareerUser.objects.bulk_update(career_obj, ["order"])
        return Response(status=status.HTTP_200_OK)

# 프로필내 포스팅
class ProfilePost(APIView):
    def get(self, request):
        user  = request.user
        param = request.GET

        target_id = param["id"]
        page      = param["page"]
        get_type  = param["type"]

        post_obj = Post.objects.select_related(
            POST_SELECTE_LIST
            ).prefetch_related(
                POST_PREFETCH_LIST
            ).order_by("-id")

        # 커리어 하나의 포스팅
        if get_type == "career":
            post_obj = post_obj.filter(career_id = target_id)
        
        # 프로필 주인의 모든 포스팅
        elif get_type == "all":
            post_obj = post_obj.filter(user_id = target_id)
        
        # 마지막 페이지 처리
        if page > post_obj.count()//COUNT_PER_PAGE+1:
            return Response(status=status.HTTP_204_NO_CONTENT)
        
        post_obj = post_obj[(page-1)*20:page*20]

        # 사용자의 좋아요 목록, 북마크 목록 비교
        post_list = list(post_obj)
        like_list = dict(Like.objects.filter(user_id=user.id, post__in=post_list).values_list("post_id", "user_id"))
        book_list = dict(BookMark.objects.filter(user_id=user.id, post_id__in=post_list).values_list("post_id", "user_id"))

        post_obj = MainPageSerializer(post_obj, many=True, read_only=True, context={"like_list":like_list, "book_list":book_list, "user_id":user.id}).data

        return Response(post_obj, status=status.HTTP_200_OK)

# 밴 관리
class Ban(APIView):
    # 추가 밴
    def post(self, request):
        user  = request.user
        param = request.GET

        ban_id = param["id"]

        banlist_obj, created = Banlist.objects.get_or_create(user_id = user.id)
        if not created:
            banlist_obj.banlist.append(int(ban_id))
        else: banlist_obj.banlist = [int(ban_id)]

        banlist_obj.save()

        # 팔로우 팔로잉 목록에서 삭제
        Loopship.objects.filter(user_id = user.id, friend_id = ban_id).delete()
        Loopship.objects.filter(user_id = ban_id, friend_id = user.id).delete()

        return Response(status=status.HTTP_200_OK)
    
    # 밴 목록
    def get(self, request):
        user = request.user

        banlist_obj = Banlist.objects.filter(user_id = user.id)
        banlist_obj = BanlistSerializer(banlist_obj).data

        return Response(banlist_obj, status=status.HTTP_200_OK)
    
    # 밴 해제
    def delete(self, request):
        user  = request.user
        param = request.GET

        target_id = param["id"]

        banlist_obj = Banlist.objects.get(user_id = user.id)
        banlist_obj.banlist.remove(int(target_id))
        banlist_obj.save()

        return Response(status=status.HTTP_200_OK)

# 신고
class ReposrtAPI(APIView):
    report_type = {
        "post"     : 1,
        "comment"  : 2,
        "cocomment": 3
    }
    
    def post(self, request):
        user  = request.user
        data  = request.data
        param = request.GET

        report_type = self.report_type[param["type"]]

        Report.objects.create(
            user_id   = user.id, 
            type      = report_type,
            target_id = data["id"],
            reason    = data["reason"]
            )
        report_count = Report.objects.filter(type=report_type, target_id=data["id"]).count()
        # 누적 3회 이상 시 운영진에게 알람
        if report_count >= 3:    
            report_alarm(report_count, data["id"], data["reason"])

        return Response(status=status.HTTP_200_OK)

# 사용자 알람
class UserAlarm(APIView):
    def get(self, request):
        user  = request.user
        param = request.GET

        get_type = param["type"]
        
        # 알람 읽음 처리리
        if get_type == "read":
            alarm_id = param["id"]
            Alarm.objects.filter(id = alarm_id).update(is_read=True)

            return Response(status=status.HTTP_200_OK)
        
        # 알람 리스트 조회
        elif get_type == "list":
            last_id = param["last"]

            # 7일 이후 알람 읽음 처리
            expired_date = datetime.datetime.now() - datetime.timedelta(days=7)
            Alarm.objects.filter(user_id = user.id, date__lte = expired_date, is_read = False).update(is_read = True)
            
            alarm_obj = Alarm.objects.filter(user_id = user.id).order_by("-id")
            # 리스트에서 마지막 알람 id 이후 20개 호출
            if last_id != "0":
                alarm_obj = alarm_obj.filter(id__lt = last_id)
            
            alarm_obj = alarm_obj[:COUNT_PER_PAGE]
            alarm_obj = AlarmSerializer(alarm_obj, many=True).data

            return Response(alarm_obj, status=status.HTTP_200_OK)
    
    def delete(self, request):
        param = request.GET

        target_id = param["id"]

        Alarm.objects.get(id = target_id).delete()

        return Response(status=status.HTTP_200_OK)

# 팔로우 관리
class Loop(APIView):
    # 팔로우
    def post(self, request):
        user  = request.user
        param = request.GET

        profile_obj = Profile.objects.get(user_id=user.id)
        loop_fcm(param["id"], profile_obj.real_name, user.id)

        Loopship.objects.create(user_id=user.id, friend_id=param["id"])
        return Response(status=status.HTTP_200_OK)
    # 언팔로우
    def delete(self, request):
        user  = request.user
        param = request.GET

        Loopship.objects.get(user_id=user.id, friend_id=param["id"]).delete()
        return Response(status=status.HTTP_200_OK)
    
    # 팔로우리스트
    def get(self, request):
        user  = request.user
        param = request.GET

        follow_type = param["type"]

        if follow_type == "following":
            loop_obj = Loopship.objects.select_related(
                        "friend__profile__department", "friend__profile__school"
                        ).filter(user_id=param["id"])

            loop_obj = list(map(lambda x: x.friend.profile, loop_obj))
        
        elif follow_type == "follower":
            loop_obj = Loopship.objects.select_related(
                        "friend__profile__department", "friend__profile__school"
                        ).filter(friend_id=param["id"])
            loop_obj = list(map(lambda x: x.user.profile, loop_obj))

        following_list = dict(Loopship.objects.filter(user_id=user.id).values_list('friend_id', 'user_id'))
        follower_list  = dict(Loopship.objects.filter(friend_id=user.id).values_list('user_id', 'friend_id'))

        loop_obj = ProfileListWithLoopSerializer(loop_obj, many=True, read_only=True, 
                    context={"user_id":user.id, "follower_list":follower_list, "following_list":following_list}
                    ).data

        return Response(loop_obj, status=status.HTTP_200_OK)

# 매월 1일 월별 태그 동향 기록
class MonthlyTag(APIView):
    def post(self, request):
        user = request.user
        if user.id != 5: return Response(status=status.HTTP_403_FORBIDDEN)

        today      = datetime.date.today()
        date_range = today-relativedelta(months=1)
        last_month = date_range.month

        post_tags = Post_Tag.objects.select_related("post", "tag").filter(
            post__date__range=[date_range, today]
        )

        tag_map = {}
        for tag in post_tags:
            if tag.tag not in tag_map: tag_map[tag.tag] = 1
            else: tag_map[tag.tag] += 1
        
        for tag in tag_map:
            tag.monthly_count[last_month] = tag_map[tag]

        Tag.objects.bulk_update(tag_map, ['monthly_count'])

        return Response(status=status.HTTP_200_OK)

# 일별 지난 7일간 인기 포스팅
class PostRanking(APIView):
    def post(self, request):
        user = request.user
        if user.id != 5: return Response(status=status.HTTP_403_FORBIDDEN)

        now = datetime.datetime.now()
        post_obj = Post.objects.filter(date__range=[now-datetime.timedelta(days=7), now]
                    ).select_related("career").order_by("-like_count", "-id")[:10]
        
        post_list = [PostingRanking(post_id=post.id, score=post.like_count) for post in post_obj]
        PostingRanking.objects.all().delete()
        PostingRanking.objects.bulk_create(post_list)

        return Response(status=status.HTTP_200_OK)

# 일별 지난 30일간 기록을 통한 유저 랭킹
class UserRanking(APIView):
    # 유저 랭킹 top N 
    def get_ranker_list(self, user, N=None):
        ranker_obj = Profile.objects.all().exclude(rank=0).order_by("rank")[:N]
        following_list = dict(Loopship.objects.filter(user_id=user.id).values_list('friend_id', 'user_id'))
        follower_list  = dict(Loopship.objects.filter(friend_id=user.id).values_list('user_id', 'friend_id'))

        ranker_obj = RankProfileListSerializer(ranker_obj, many=True, read_only=True, 
                        context={"user_id":user.id, "follower_list":follower_list, "following_list":following_list}
                        ).data
        return ranker_obj

    def post(self, request):
        user = request.user
        if user.id != 5: return Response(status=status.HTTP_403_FORBIDDEN)

        now = datetime.datetime.now()

        profile_obj = Profile.objects.filter(type=0)
        # 점수 = 좋아요X3 + 조회수X1 + 포스팅수X5
        profile_obj = Profile.objects.prefetch_related('user__post'
                      ).filter(type=0, user__post__date__range=[now-datetime.timedelta(days=90), now]
                      ).annotate(calc_score=ExpressionWrapper(
                        Sum('user__post__like_count')*5+Sum('user__post__view_count')+Count('user__post')*3, 
                        output_field=SmallIntegerField())
                      ).order_by('-calc_score')
        
        accN = 0
        score = 0
        school_dict = {}
        school_list = Profile.objects.filter(type=0).values('school_id').distinct()
        for school in school_list:
            school_dict[school['school_id']] = {'accN':0, 'score':0, 'rank':1}
        
        profile_obj = Profile.objects.filter(type=0).order_by("-score")
        # 전국, 교내 순위 계산
        for i , profile in enumerate(profile_obj, 1):
            profile.last_rank = profile.rank
            # 공동 순위를 위한 계산
            if profile.calc_score != score: 
                profile.rank = i
                score        = profile.calc_score
                accN         = 0
            else: 
                accN         += 1
                profile.rank = i - accN

            profile.school_last_rank = profile.school_rank
            school_rank = school_dict[profile.school_id]
            if profile.calc_score != school_rank['score']:
                profile.school_rank = school_rank['rank']
                school_rank['rank'] += 1
                school_rank['score'] = profile.calc_score
                school_rank['accN'] = 0
            else:
                school_rank['accN'] += 1
                profile.school_rank = school_rank['rank'] - school_rank['accN']

        Profile.objects.bulk_update(profile_obj, ["rank", "last_rank", "school_rank", "school_last_rank"])  
        
        return Response(status=status.HTTP_200_OK)
    
    def get(self, request):
        user  = request.user
        param = request.GET

        get_type = param["type"]

        # 커리어 보드 main
        if get_type == "main":
            # 인기 포스팅
            post_obj = PostingRanking.objects.all().select_related(
                ["post__" + _ for _ in POST_SELECTE_LIST]
                ).prefetch_related(
                    ["post__"+ _ for _ in POST_PREFETCH_LIST]
                )

            post_obj = list(map(lambda x:x.post, post_obj))
            post_obj = MainPageSerializer(post_obj, many=True, read_only=True).data

            # 상위 랭커            
            ranker_obj = self.get_ranker_list(user, 3)
            return Response({"posting":post_obj, "ranking":ranker_obj}, status=status.HTTP_200_OK)
        
        # 순위 리스트 top50
        else:
            ranker_obj = self.get_ranker_list(user, 50)
            return Response(ranker_obj, status=status.HTTP_200_OK)

class HotStudent(APIView):
    def post(self, request):
        user = request.user
        if user.id != 5: return Response(status=status.HTTP_403_FORBIDDEN)

        now = datetime.datetime.now()
        
        post_obj = Post.objects.filter(
                    date__range = [now-datetime.timedelta(days=7), now]
                    ).values("user_id"
                    ).annotate(Sum("like_count")).order_by("-like_count__sum")[:20]

        hotstudent_list = [HotUser(user_id=post["user_id"]) for post in post_obj]
        HotUser.objects.all().delete()
        HotUser.objects.bulk_create(hotstudent_list)

        return Response(status=status.HTTP_200_OK)
    
    def get(self, request):
        user_obj = HotUser.objects.all().select_related(["user__profile__" + _ for _ in PROFILE_SELECT_LIST])
        user_obj = list(map(lambda x: x.user.profile, user_obj))
        user_obj = RankProfileListSerializer(user_obj, many=True, read_only=True).data
        return Response(user_obj, status=status.HTTP_200_OK)