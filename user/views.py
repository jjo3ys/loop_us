from django.contrib.auth import authenticate
from django.contrib.auth.models import User
from django.contrib.auth.hashers import check_password
from django.core.paginator import Paginator
from django.core.mail import EmailMessage, EmailMultiAlternatives
from django.utils import timezone
from django.db.utils import IntegrityError

from rest_framework.response import Response
from rest_framework.decorators import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.authtoken.models import Token
from rest_framework import status

from .utils import ES, CLIENT, send_msg
from .models import *

from career.utils import delete_tag
from career.models import *

# 인증번호 확인
class Activate(APIView):
    def post(self, request):
        data        = request.data
        user_obj    = User.objects.filter(username=email)
        
        email       = data['eamil']
        certify_num = data['certify_num']
        
        num         = CLIENT.get(email.replace('@', ''))
        num         = str(num, 'utf-8')
        
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
        
        is_create = int(param['is_create'])
        email     = data['email']
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
        email     = data['email']
        pwd       = data['password']
        
        real_name = data['real_name']
        dep_id    = data['department']
        school_id = data['school']
        admission = data['admission']
        type      = data['type']
        
        user_obj = User.objects.create_user(
            username = email,
            email    = email,
            password = pwd
        )
        token_obj = Token.objects.create(
            user=user_obj
        )
        try:
            profile_obj = Profile.objects.create(
                user          = user_obj,
                real_name     = real_name,
                department_id = dep_id,
                school_id     = school_id,
                admission     = admission,
                type          = type
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
        ES.index(index='profile', doc_type='_doc', body=body)
        
        if not int(type):                                                                                               # 학생 계정일 때만 기본 커리어 생성
            career_obj = Career.objects.create(
                career_name = '나만의 커리어',
                is_public   = False
            )
            CareerUser.objects.create(
                user   = user_obj,
                career = career_obj
            )
            
        loop_list = list()                                                                                              # 생성시 같은 학과 내 계정들 다 팔로우&팔로잉
        loopers = Profile.objects.filter(
            department_id = dep_id
        ).exclude(user_id = user_obj.id)
        for looper in loopers:
            loop_list.append(Loopship(
                user_id=user_obj.id, 
                friend_id=looper.user_id
                ))
            loop_list.append(Loopship(
                user_id=looper.user_id,
                friend_id=user_obj.id
                ))
        Loopship.objects.bulk_create(loop_list)
        
        return Response(data={
            'token'        : token_obj.key,
            'school_id'    : 'school'+str(school_id),
            'department_id': 'department'+str(dep_id),
            'is_student'   : 1,
            'user_id'      : str(user_obj.id)
        }, status=status.HTTP_201_CREATED)

# 회원 탈퇴
class Resign(APIView):
    def post(self, request):
        user_obj = request.user
        data     = request.data
        
        reason   = data['reason']
        
        profile_obj = Profile.objects.select_related('department', 'school').get(user_id = user_obj.id)
        profile_obj.profile_image.delete(save=False)
        
        message = EmailMessage(
            subject = f'{profile_obj.real_name}님 탈퇴 사유',
            body    = f'{profile_obj.school.school} {profile_obj.department.department} \n 사유 : {reason}',
            to      = ['loopus@loopus.co.kr']
        )
        
        try:
            message.send()
        except: return Response(status=status.HTTP_406_NOT_ACCEPTABLE)

        careerUser_obj = CareerUser.objects.filter(user_id=user_obj.id)
        career_list = list(careerUser_obj.values_list('career_id', flat=True))
        career_dict = dict(Career.objects.filter(
            id__in=career_list, 
            is_public=True, 
            tag_company=False).exclude(thumnail=None).values_list('thumbnail', flat=True))
        
        post_obj = Post.objects.filter(user_id=user_obj.id).prefetch_related('contents_image', 'contents_file')
        for post in post_obj:
            for image in post.contents_image.all():
                if image.id in career_dict:
                    post.career.thumbnail = None
                    post_list = Post.objects.filter(career_id=post.career_id).exclude(id=post.id)
                    post_image_obj = PostImage.objects.filter(post__in=post_list)             
                    if post_image_obj.exists():
                        post.career.thumbnail = post_image_obj.last().id               
                    post.career.save()
                image.image.delete(save=False)
            
            for file in post.contents_file.all():
                file.file.delete(save=False)
                 
        career_list = list(careerUser_obj.filter(is_manager=1).values_list('career_id', flat=True))
        Career.objects.filter(id__in=career_list).delete()
        
        tag_obj = Post_Tag.objects.filter(post___in=post_obj)
        delete_tag(tag_obj)
        
        ES.delete_by_query(index='profile', doc_type='_doc', body={'query':{'match':{"user_id":{"query":request.user.id}}}})
        user = User.objects.filter(id=user_obj.id)
        user.delete()
        
        return Response(status=status.HTTP_200_OK)

#로그인   
class Login(APIView):
    def post(self, request):
        data     = request.data
        
        username = data['username']
        password = data['password']
        
        user_obj = authenticate(
            username = username,
            password = password
        )
        
        if user_obj and user_obj.is_active:
            token_obj = Token.objects.get(user_id = user_obj.id)
            
            user_obj.last_login = timezone.now()
            user_obj.save()
            
            profile_obj = Profile.objects.filter(user_id = user_obj.id)
            if profile_obj.exists():
                profile_obj = profile_obj.first()
                topic_list = list(CareerUser.objects.select_related('career')
                                  .filter(user_id=user_obj.id, career__is_public=True)
                                  .values_list('career_id', flat=True))
                return Response(data={
                    'token'        : token_obj.key,
                    'school_id'    : 'school' + str(profile_obj.school_id),
                    'department_id': 'department' + str(profile_obj.department_id),
                    'topic_list'   : topic_list,
                    'user_id'      : str(user_obj.id),
                    'is_student'   : 1
                }, status=status.HTTP_202_ACCEPTED)
            
            else:
                return Response(data={
                    'token'     : token_obj.key,
                    'user_id'   : str(user_obj.id),
                    'is_student': 0
                })

#비밀번호 관련               
class Password(APIView):
    def put(self, request):
        user  = request.user
        param = request.GET
        data  = request.data
        
        type  = param['type']
        
        if type == 'change' and check_password(data['origin_pw'], user.password): # 비밀번호 변경
            user.set_password(data['origin_pw'])
            user.save()
            return Response(status=status.HTTP_200_OK)
        
        elif type == 'find':                                                      # 인증 완료 후 비밀번호 설정
            try: user = User.objects.get(email=data['email'])
            except: return Response(status=status.HTTP_401_UNAUTHORIZED)
            
            user.set_password(data['password'])
            user.save()
            return Response(status=status.HTTP_200_OK)
        return Response(status=status.HTTP_401_UNAUTHORIZED)
    
    def post(self, request):                                                      # 비밀번호 찾기 인증
        data  = request.data     
         
        email = data['email']
        
        try: user = User.objects.get(email=email)
        except: return Response(status=status.HTTP_401_UNAUTHORIZED)
        user.is_active = False
        user.save()
        return Response(status=status.HTTP_200_OK)
    
# 문의
class Ask(APIView):
    mail = {
        'school'         : '학교 등록 문의',
        'department'     : '학과 등록 문의',
        'comapny_signup' : '기업 회원가입 문의',
        'company_info'   : '기업 소개 수정 문의',
    }
    def post(self, request):
        param     = request.GET
        data      = request.data
        
        type      = param['type']
        
        if type == 'normal':
            message = EmailMessage(
                subject = f'{data["real_name"]}님 문의',
                body    = f'이메일:{data["email"]}\n\
                            문의내용:{data["content"]}\n\
                            기기:{data["device"]}\n\
                            OS버전:{data["os"]}\n\
                            빌드번호:{ data["app_ver"]}\n\
                            유저id:{data["id"]}',
                to      = ['loopus@loopus.co.kr']
            )
        
        elif type == 'school':
            message = EmailMessage(
                subject = '학교 등록 문의',
                body    =
            )