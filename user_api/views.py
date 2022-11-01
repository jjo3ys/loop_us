# import os
# from django.shortcuts import redirect
from django.contrib.auth import authenticate
from django.contrib.auth.models import User
from django.contrib.auth.hashers import check_password
from django.core.paginator import Paginator
# for email check
# from django.conf.global_settings import SECRET_KEY

from django.core.mail import EmailMessage, EmailMultiAlternatives
from django.utils import timezone
# from django.utils.http import (
#     urlsafe_base64_encode,
#     urlsafe_base64_decode,
# )
# from django.utils.encoding import (
#     force_bytes,
#     force_text
# )
from django.db.utils import IntegrityError

from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.authtoken.models import Token
from rest_framework import status

from fcm.push_fcm import report_alarm
from post_api.serializers import MainloadSerializer

# from .department import DEPARTMENT
from .models import InterestCompany, Profile, Activation, Company_Inform, Banlist, Report, Alarm, UserSNS, ViewCompany
from .serializers import AlarmSerializer, BanlistSerializer, CompanyProfileSerializer, ProfileSerializer, SimpleProfileSerializer, ViewProfileSerializer

# from search.models import Get_log, InterestTag
from tag.models import Post_Tag
from project_api.models import Project, ProjectUser
from project_api.serializers import OnlyProjectUserSerializer
from post_api.models import BookMark, Like, Post
from loop.models import Loopship
# from fcm.models import FcmToken
from chat.models import Room, Msg

from elasticsearch import Elasticsearch

# import jwt
import json
import redis
import datetime
import requests
# import platform
import random

headers = {
    'Accpet':'application/json',
    'Authorization':'frbSEAcXD+a6UEOUq1lkWcWmFoDku20SZvLeO++pP9e5yQo5GIqTkbVbctqafewScJuzLLcTW/l4d/Lw/wjOig==',
    'Content-Type': 'application/json',
}

params = (
    ('serviceKey', 'frbSEAcXD+a6UEOUq1lkWcWmFoDku20SZvLeO++pP9e5yQo5GIqTkbVbctqafewScJuzLLcTW/l4d/Lw/wjOig=='),
)

client = redis.Redis()

def delete_tag(tag_obj):
    for tag in tag_obj:
        tag.tag.count = tag.tag.count-1
        if tag.tag.count == 0:
            try:
                tag.tag.delete()
            except IntegrityError:
                pass
        else:
            tag.tag.save()

def send_msg(email):
    r = client.get(email.replace('@', ''))
    if not r:
        pass
    else:
        client.delete(email)
    certify_num = ''
    for i in range(6):
        certify_num += str(random.randint(0, 9))
    main_title = 'LOOP US 이메일 인증'
    html_content = f'<h5>아래 인증 번호를 앱에서 입력해 주세요.</h5>\
                     <h3>{certify_num}</h3>\
                     <h5>감사합니다.</h5>'
    mail_to = email
    msg = EmailMultiAlternatives(main_title, "아래 인증 번호를 앱에서 입력해 주세요.", to=[mail_to])
    msg.attach_alternative(html_content, "text/html")
    msg.send()
    client.set(email.replace('@', ''), certify_num, datetime.timedelta(seconds=180))

@api_view(['POST', ])
def activate(request):
    email = request.data['email']
    certify_num = request.data['certify_num']
    r = client.get(email.replace('@', ''))
    if str(r, 'utf-8') == certify_num:
        client.delete(email)
        user = User.objects.filter(username=email)
        if user.exists():
            user = user[0]
            user.is_active = True
            user.save()
        else:
            pass
        return Response(status=status.HTTP_200_OK)
    else: return Response(status=status.HTTP_401_UNAUTHORIZED)

# def send_msg(email):
#     r = client.get(email.replace('@', ''))
#     if not r:
#         pass
#     else:
#         client.delete(email)
#     if platform.system() == 'Linux':
#         token = jwt.encode({'id': email}, SECRET_KEY, algorithm='HS256').decode('utf-8')# ubuntu환경
#     else:
#         token = jwt.encode({'id': email}, SECRET_KEY, algorithm='HS256')
#     html_content = f'<h3>아래 링크를 클릭하시면 인증이 완료됩니다.</h3><br>\
#                      <a href="http://3.35.253.151:8000/user_api/activate/{token}">이메일 인증 링크</a><br><br>\
#                      <h3>감사합니다.</h3>'

#     main_title = 'LOOP US 이메일 인증'
#     mail_to = email
#     msg = EmailMultiAlternatives(main_title, "아래 링크를 클릭하여 인증을 완료해 주세요.", to=[mail_to])
#     msg.attach_alternative(html_content, "text/html")
#     msg.send()
#     client.set(email.replace('@', ''), 0, datetime.timedelta(seconds=180))

@api_view(['POST'])
def certification(request):
    for_create = int(request.GET['is_create'])
    if for_create and User.objects.filter(username=request.data['email']).exists():       
        return Response(status=status.HTTP_400_BAD_REQUEST)
    send_msg(request.data['email'])
    return Response(status=status.HTTP_200_OK)

# @api_view(['GET', ])
# def activate(request, token):
#     try:
#         user_dic = jwt.decode(token, algorithms='HS256')
#         email = user_dic['id']
#         email = email.replace('@', '')
#         r =  client.get(email)
#         if int(r) == 0:
#             client.delete(email)
#             user = User.objects.filter(username=user_dic['id'])
#             if user.exists():
#                 user = user[0]
#                 user.is_active = True
#                 user.save()
#             else:
#                 pass
#             certify_fcm(email)
#             return redirect("https://loopusimage.s3.ap-northeast-2.amazonaws.com/static/email_authentification_success.png")
#     except:
#         return redirect("https://loopusimage.s3.ap-northeast-2.amazonaws.com/static/email_authentification_fail.png")

@api_view(['POST', ])
def check_corp_num(request):
    data = {"b_no":["{0}".format(request.data['corp_num'])]}
    data = json.dumps(data)
    res = requests.post('http://api.odcloud.kr/api/nts-businessman/v1/status',
                        headers=headers, 
                        params=params, 
                        data=data)

    if res.json()['data'][0]['tax_type'] == '국세청에 등록되지 않은 사업자등록번호입니다.':
        return Response("국세청에 등록되지 않은 사업자등록번호입니다.", status=status.HTTP_203_NON_AUTHORITATIVE_INFORMATION)              
    
    else:
        try:
            user = User.objects.create_user(username=request.data['username'],
                                            password=request.data['password'],
                                            email=request.data['email'],
                                            is_active=False)
        except IntegrityError:
            return Response("이미 있는 아이디 입니다.", status=status.HTTP_401_UNAUTHORIZED)

        Activation.objects.create(user_id = user.id,
                                  corp_num = request.data['corp_num'],
                                  corp_name = request.data['corp_name'],
                                  email = request.data['email'],
                                  name = request.data['name'],
                                  tel_num = request.data['tel_num'])

        return Response("인증 대기중입니다.", status=status.HTTP_200_CREATED)

@api_view(['POST'])
def signup(request):
    type = request.data['type']

    if int(type) == 1:
        user = User.objects.create_user(username=request.data['username'], email=request.data['username'], password=request.data['password'], is_active=True)
    else:
        user = User.objects.create_user(username=request.data['email'], email=request.data['email'], password=request.data['password'], is_active=True)
    
    token = Token.objects.create(user_id=user.id)
    try:
        profile_obj = Profile.objects.create(user_id = user.id,
                                            type = type,
                                            real_name = request.data['real_name'],
                                            profile_image = None,
                                            department_id = request.data['department'],
                                            school_id = request.data['school'],
                                            admission = request.data['admission'])
        es = Elasticsearch()
        body = {
            "user_id":user.id,
            "text":profile_obj.school.school + " " + profile_obj.department.department + " " + profile_obj.real_name
        }
        es.index(index='profile', doc_type='_doc', body=body)
    except:
        es.delete_by_query(index='profile', doc_type='_doc', body={'query':{'match':{"user_id":{"query":user.id}}}})
        token.delete()
        user.delete()
        return Response('Profile information is not invalid', status=status.HTTP_404_NOT_FOUND)

    if type == 1:
        corp = Activation.objects.filter(user_id=user.id)[0]
        Company_Inform.objects.create(profile_id = profile_obj.id,
                                    corp_num = corp.corp_num,
                                    corp_name = corp.corp_name)
        corp.delete()
        return Response({'token':token.key,
                        'is_student':0,
                        'user_id':str(token.user_id)}, status=status.HTTP_201_CREATED)
    else:
        loop_list = []
        dep_loop = Profile.objects.filter(department_id=request.data['department']).exclude(user_id=user.id)
        for looper in dep_loop:
            loop_list.append(Loopship(user_id=user.id, friend_id=looper.user_id))
            loop_list.append(Loopship(user_id=looper.user_id, friend_id=user.id))
        Loopship.objects.bulk_create(loop_list)
    # InterestTag.objects.create(user_id=user.id, tag_list={})
        return Response({'token':token.key,
                        'school_id':'school'+str(profile_obj.school_id),
                        'department_id':'department'+str(profile_obj.department_id),
                        'is_student':1,
                        'user_id':str(token.user_id)}, status=status.HTTP_201_CREATED)
    
@api_view(['POST'])
def login(request):
    user = authenticate(
    username=request.data['username'],
    password=request.data['password'],
    )
    if user is not None and user.is_active:
        token_obj = Token.objects.filter(user_id=user.id)[0]
        user.last_login = timezone.now()
        user.save()
        if Company_Inform.objects.filter(user_id=user.id).exists(): 
            return Response({'token':token_obj.key,
                            'is_student':0,
                            'user_id':str(token_obj.user_id)}, status=status.HTTP_202_ACCEPTED)

        else:    
            profile_obj = Profile.objects.filter(user_id=user.id)[0]
            
            return Response({'token':token_obj.key,
                            'school_id':'school'+str(profile_obj.school_id),
                            'department_id':'department'+str(profile_obj.department_id),
                            'is_student':1,
                            'user_id':str(token_obj.user_id)}, status=status.HTTP_202_ACCEPTED)
    
    else:
        return Response("인증 만료 로그인 불가",status=status.HTTP_401_UNAUTHORIZED)
    
@api_view(['PUT', 'POST'])
def password(request):
    if request.method == 'PUT':
        if request.GET['type'] == 'change':
            user = request.user
            
            if check_password(request.data['origin_pw'], user.password):
                new_pw = request.data['new_pw']
                user.set_password(new_pw)
                user.save()
                return Response("pw is changed", status=status.HTTP_200_OK)
            else:
                return Response("origin_pw is not matched with data", status=status.HTTP_401_UNAUTHORIZED)

        elif request.GET['type'] == 'find':
            try:
                user = User.objects.filter(email=request.data['email'])[0]
                user.set_password(request.data['password'])
                user.save()
                return Response(status=status.HTTP_200_OK)

            except IndexError:
                return Response(status=status.HTTP_401_UNAUTHORIZED)

    elif request.method =='POST':
        try:
            user = User.objects.filter(email=request.data['email'])[0]
            user.is_active = False
            user.save()
            send_msg(request.data['email'])
        except IndexError:
                return Response(status=status.HTTP_401_UNAUTHORIZED)

        return Response(status=status.HTTP_200_OK)
    
@api_view(['POST', ])
@permission_classes((IsAuthenticated,))
def resign(request):   
    user = request.user
    profile_obj = Profile.objects.filter(user_id=user.id).select_related('department', 'school')[0]
    profile_obj.profile_image.delete(save=False)
    message = EmailMessage('{}님 탈퇴 사유'.format(profile_obj.real_name), '{} {} \n 사유:{}'.format(profile_obj.school.school, profile_obj.department.department, request.data['reason']), to=['loopus@loopus.co.kr'])
    try:
        message.send()
    except:
        return Response(status=status.HTTP_406_NOT_ACCEPTABLE)

    # try:
    #     intereset_list = InterestTag.objects.filter(user_id=user.id)[0]
    #     intereset_list.delete()
    # except:
    #     pass
    project_obj = ProjectUser.objects.filter(user_id=user.id)
    project_list = list(project_obj.values_list('project_id', flat=True))
        
    for post in Post.objects.filter(project_id__in=project_list).prefetch_related('contents_image'):
        for image in post.contents_image.filter(post_id=post.id):
            image.image.delete(save=False)
    
    project_list = list(project_obj.filter(is_manager=1).values_list('project_id', flat=True))
    Project.objects.filter(id__in=project_list).delete()

    tag_obj = Post_Tag.objects.filter(post__in=Post.objects.filter(user_id=user.id))
    delete_tag(tag_obj)
    es = Elasticsearch()
    es.delete_by_query(index='profile', doc_type='_doc', body={'query':{'match':{"user_id":{"query":request.user.id}}}})
    user = User.objects.filter(id=user.id)[0]
    user.delete()
    return Response("resign from loop", status=status.HTTP_200_OK)  

@api_view(['POST', ])
def ask(request):
    type = request.GET['type']
    if type == 'normal':
        message = EmailMessage('{}님 문의'.format(request.data['real_name']), '이메일:{} \n 문의내용:{} \n 기기:{} \n OS버젼:{} \n 빌드번호:{} \n 유저id:{}'.format(request.data['email'],
                                                                                                                                                            request.data['content'],
                                                                                                                                                            request.data['device'],
                                                                                                                                                            request.data['os'],
                                                                                                                                                            request.data['app_ver'],
                                                                                                                                                            request.data['id']), to=['loopus@loopus.co.kr'])
    elif type == 'school':
        message = EmailMessage('학교 등록 문의', '문의 내용: {}'.format(request.data['content']))
    elif type == 'department':
        message = EmailMessage('{} 학과 등록 문의'.format(request.data['school']), '문의 내용: {}'.format(request.data['content']))
    elif type == 'company_signup':
        message = EmailMessage('{} 기업 회원가입 문의'.format(request.data['company_name']), '첨부된 파일의 양식에 따라 작성하여 다시 보내주시면 검토하여 등록 후 이 메일을 통해 알려드리겠습니다.', to=[request.data['email']])
        message.attach_file('signup_form.csv')
    elif type == 'company_info':
        message = EmailMessage('{} 기업 소개 수정 문의'.format(request.data['company_name']), '첨부된 파일의 양식에 따라 작성하여 다시 보내주시면 검토하여 등록 후 이 메일을 통해 알려드리겠습니다.', to=[request.data['email']])
        message.attach_file('edit_information_form.csv')
    try:
        message.send()
        return Response(status=status.HTTP_200_OK)
    except:
        return Response(status=status.HTTP_406_NOT_ACCEPTABLE)
    
@api_view(['GET', 'PUT'])
@permission_classes((IsAuthenticated,))
def companyProfile(request):
    if request.method == 'GET':
        # try:
            user = request.user
            company_id = int(request.GET['id'])
            crop_obj = Company_Inform.objects.filter(user_id=company_id)[0]
    
            is_student = int(request.GET['is_student'])
            if is_student:
                crop_obj.view_count += 1
                crop_obj.save()

                viewd, created = ViewCompany.objects.get_or_create(user = user, shown_id = company_id)
                if not created:
                    viewd.date = datetime.datetime.now()
                    viewd.save()
                
                interest_obj, created = InterestCompany.objects.get_or_create(user_id=user.id, company=company_id)
                if not created:
                    interest_obj.delete()
                    InterestCompany.objects.create(user_id=user.id, company=company_id)

            company_obj = CompanyProfileSerializer(crop_obj).data
            follow_obj = Loopship.objects.filter(user_id=user.id, friend_id=company_id)
            following_obj = Loopship.objects.filter(user_id=company_id, friend_id=user.id)

            if user.id == company_id:
                company_obj.update({"is_user":1})
                company_obj.update({"follow_count":follow_obj.count(), "following_count":following_obj.count()})

            else:
                if Banlist.objects.filter(user_id=user.id, banlist__contains=int(company_id)).exists() or Banlist.objects.filter(user_id=company_id, banlist__contains=user.id).exists():
                    return Response(status=status.HTTP_204_NO_CONTENT) 
                company_obj.update({"is_user":0})
                if follow_obj.exists() and following_obj.exists():
                    company_obj.update({'looped':3})
                elif follow_obj.exists():
                    company_obj.update({'looped':2})
                elif following_obj.exists():
                    company_obj.update({'looped':1})
                else:
                    company_obj.update({'looped':0})
                    
            interest_obj = list(InterestCompany.objects.filter(company=company_id).order_by('-id').values_list('user_id', flat=True))[:20]
            std_profile = SimpleProfileSerializer(Profile.objects.filter(user_id__in=interest_obj).select_related('school', 'department'), many=True).data
            company_obj.update({'interest':std_profile})

            return Response(company_obj, status=status.HTTP_200_OK)

        # except:
        #     return Response(status=status.HTTP_404_NOT_FOUND)

@api_view(['GET'])
@permission_classes((IsAuthenticated,))
def view_list(request):
    if request.GET['type'] == 'all':

        company_show = list(ViewCompany.objects.filter(user = request.user).order_by('-date').values_list('shown_id', flat=True)[:3])
        show_crop_info = list(ViewCompany.objects.filter(shown_id = request.user).order_by('-date').values_list('user_id', flat=True)[:3])

        view = SimpleProfileSerializer(Profile.objects.filter(user_id__in=company_show), many=True).data
        viewd = SimpleProfileSerializer(Profile.objects.filter(user_id__in=show_crop_info), many=True).data

        return Response({"show":view, "shown":viewd}, status=status.HTTP_200_OK)

    else:
        profile_list = []

        if request.GET['type'] == 'shown':  # 최근 루프어스가 조회한 프로필 
            view_obj = Paginator(ViewCompany.objects.filter(user = request.user).order_by('-date'), 15)

        elif request.GET['type'] == 'user': # 최근 루프어스를 조회한 프로필
            view_obj = Paginator(ViewCompany.objects.filter(shown_id = request.user).order_by('-date'), 15)

        if view_obj.num_pages < int(request.GET['page']):
                return Response(status=status.HTTP_204_NO_CONTENT)

        views = ViewProfileSerializer(view_obj.get_page(request.GET['page']), many = True).data   
        profile_list = list(a[request.GET['type']] for a in views)
        
        return Response(SimpleProfileSerializer(Profile.objects.filter(user_id__in=profile_list), many=True).data, status=status.HTTP_200_OK)

@api_view(['PUT', 'GET', 'DELETE'])
@permission_classes((IsAuthenticated,))
def profile(request):
    profile_obj = Profile.objects.select_related('department', 'school').filter(user_id=request.user.id)[0]
    if request.method == 'PUT':
        type = request.GET['type']
        if type == 'image':
            profile_obj.profile_image.delete(save=False)
            profile_obj.profile_image = request.FILES.get('image')
            profile_obj.save()

        elif type == 'sns':
            type_id = request.data['type']
            sns_obj = UserSNS.objects.filter(profile_id=profile_obj.id, type=type_id)
            if sns_obj.exists():
                sns_obj.update(url=request.data['url'])
            else:
                UserSNS.objects.create(profile_id=profile_obj.id, type=type_id, url=request.data['url'])

        elif type == 'profile':
            email = request.data['email']           
            user_obj = User.objects.filter(user_id=request.user.id)[0]
            user_obj.username = email
            user_obj.email = email
            
            profile_obj.real_name = request.data['real_name']
            profile_obj.school_id = request.data['school']
            profile_obj.department_id = request.data['department']
            profile_obj.admission = request.data['admission']
            profile_obj.rank, profile_obj.last_rank, profile_obj.school_rank, profile_obj.school_last_rank = 0
            es = Elasticsearch()
            es.delete_by_query(index='profile', doc_type='_doc', body={'query':{'match':{"user_id":{"query":request.user.id,}}}})
            body = {
                "user_id":request.user.id,
                "text":profile_obj.school.school + " " + profile_obj.department.department + " " + profile_obj.real_name
            }
            es.index(index='profile', doc_type='_doc', body=body)
            
            user_obj.save()
            profile_obj.save()
            
        return Response(ProfileSerializer(profile_obj).data, status=status.HTTP_200_OK)
        
    elif request.method == 'DELETE':
        type = request.GET['type']
        if type == 'sns':
            UserSNS.objects.filter(id=request.GET['id']).delete()
        elif type == 'image':
            profile_obj = Profile.objects.filter(user_id=request.GET['id'])[0]
            profile_obj.profile_image.delete(save=False)
            profile_obj.save()
        
        return Response(status=status.HTTP_200_OK)

    elif request.method == 'GET':
        idx = request.GET['id']
        is_student = int(request.GET['is_student'])
        
        if not is_student:
            view_obj, created = ViewCompany.objects.get_or_create(user = request.user, shown_id = idx)          
            if not created:
                view_obj.date = datetime.datetime.now()
                view_obj.save()

        try:
            profile_obj = Profile.objects.select_related('department', 'school').filter(user_id=idx)[0]
            profile = ProfileSerializer(profile_obj).data
        except:
            return Response(status=status.HTTP_404_NOT_FOUND)

        if str(request.user.id) == idx:
            profile.update({'is_user':1})
            if Alarm.objects.filter(user_id=request.user.id, is_read=False).exists():
                profile.update({'new_alarm':True})
            else:
                profile.update({'new_alarm':False})

            if Msg.objects.filter(room__in=Room.objects.filter(member__icontains=request.user.id), receiver_id=request.user.id, is_read=False).exists():
                profile.update({'new_message':True})
            else:
                profile.update({'new_message':False})
            
        else:
            if Banlist.objects.filter(user_id=request.user.id, banlist__contains=int(idx)).exists() or Banlist.objects.filter(user_id=idx, banlist__contains=request.user.id).exists():
                return Response(status=status.HTTP_204_NO_CONTENT)
            # Get_log.objects.create(user_id=request.user.id, target_id=idx, type=1)
            profile_obj.view_count += 1
            profile_obj.save()

            profile.update({'is_user':0})
            

        follow = Loopship.objects.filter(user_id=request.user.id, friend_id=idx).exists()
        following = Loopship.objects.filter(user_id=idx, friend_id=request.user.id).exists()

        if follow and following:
            profile.update({'looped':3})
        elif follow:
            profile.update({'looped':2})#프로필 주인을 follow
        elif following:
            profile.update({'looped':1})#프로필 주인이 나를 following
        else:
            profile.update({'looped':0})

        group_count = Profile.objects.filter(group=profile_obj.group).count()
        school_count = Profile.objects.filter(school=profile_obj.school, group=profile_obj.group).count()

        group_ratio = round(profile_obj.rank/group_count, 2)
        last_group_ratio = round(profile_obj.last_rank/group_count, 2)

        school_ratio = round(profile_obj.school_rank/school_count, 2)
        school_last_ratio = round(profile_obj.school_last_rank/school_count, 2)

        profile.update({"group_ratio":group_ratio, "group_rank_variance":last_group_ratio-group_ratio,
                        "school_ratio":school_ratio, "school_rank_variance":school_last_ratio-school_ratio})
        
        return Response(profile, status=status.HTTP_200_OK)

@api_view(['POST', 'GET'])
@permission_classes((IsAuthenticated,))
def project(request):
    if request.method == 'POST':
        project_obj = ProjectUser.objects.filter(user_id=request.user.id)
        for project in project_obj:
            try:
                project.order = request.data[str(project.project_id)]
            except: continue
        ProjectUser.objects.bulk_update(project_obj, ['order'])
        
        return Response(status=status.HTTP_200_OK)

    elif request.method == 'GET':
        idx = request.GET['id']
        try:
            project_obj = ProjectUser.objects.filter(user_id=idx).select_related('project').order_by('order')
        except:
            return Response(status=status.HTTP_404_NOT_FOUND)
        project_obj = OnlyProjectUserSerializer(project_obj, many=True).data

        return Response(project_obj, status=status.HTTP_200_OK)

@api_view(['GET', ])
@permission_classes((IsAuthenticated,))
def posting(request):
    user_id = request.user.id
    page = int(request.GET['page'])
    idx = int(request.GET['id'])
    if request.GET['type'] == 'career':
        post_obj = Post.objects.filter(project_id=idx).select_related('project').order_by('-id')
    elif request.GET['type'] == 'all':
        post_obj = Post.objects.filter(user_id=idx).select_related('project').order_by('-id')
        
    if page > post_obj.count()//20+1:
        return Response(status=status.HTTP_204_NO_CONTENT)
    
    post_obj = post_obj[(page-1)*20:page*20]
    post_list = list(post_obj.values_list('id', flat=True))
    like_list = dict(Like.objects.filter(user_id=user_id, post_id__in=post_list).values_list('post_id', 'user_id'))
    book_list = dict(BookMark.objects.filter(user_id=user_id, post_id__in=post_list).values_list('user_id', 'post_id'))
    post_obj = MainloadSerializer(post_obj, many=True, read_only=True).data

    for p in post_obj:
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

    return Response(post_obj, status=status.HTTP_200_OK)

@api_view(['POST'])
@permission_classes((IsAuthenticated,))
def report_profile(request):
    Report.objects.create(user_id=request.user.id, type=0, target_id=request.data['id'], reason=request.data['reason'])
    count = Report.objects.filter(type=0, target_id=request.data['id']).count()
    if count >= 3:
        report_alarm(count, 0, request.data['id'], request.data['reason'])
    return Response(status=status.HTTP_200_OK)

@api_view(['POST', 'DELETE', 'GET'])
@permission_classes((IsAuthenticated,))
def ban(request):
    if request.method == 'POST':
        banlist_obj, valid = Banlist.objects.get_or_create(user_id=request.user.id)
        if not valid:
            banlist_obj.banlist.append(int(request.GET['id']))

        else:
            banlist_obj.banlist = [int(request.GET['id'])]

        banlist_obj.save() 
        try:
            Loopship.objects.filter(user_id=request.user.id, friend_id=request.GET['id']).delete()
        except:
            pass

        try:
            Loopship.objects.filter(user_id=request.GET['id'], friend_id=request.user.id).delete()
        except:
            pass

        return Response(status=status.HTTP_200_OK)
    
    elif request.method == 'DELETE':
        banlist_obj = Banlist.objects.filter(user_id=request.user.id)[0]
        banlist_obj.banlist.remove(int(request.GET['id']))
        banlist_obj.save()
        return Response(status=status.HTTP_200_OK)

    elif request.method == 'GET':
        try:
            banlist_obj = Banlist.objects.filter(user_id=request.user.id)[0]
        except:
            return Response(status=status.HTTP_404_NOT_FOUND)
        return Response(BanlistSerializer(banlist_obj).data, status=status.HTTP_200_OK)

@api_view(['GET', 'DELETE'])
@permission_classes((IsAuthenticated,))
def alarm(request):
    if request.method == 'GET':
        if request.GET['type'] == 'read':
            alarm_obj = Alarm.objects.filter(target_id=request.GET['id'], type=request.GET['type_id'], alarm_from_id=request.GET['sender_id'])[0]
            alarm_obj.is_read = True
            alarm_obj.save()

            return Response(status=status.HTTP_200_OK)
        
        else:            
            if request.GET['last'] == '0':
                alarm_obj = Alarm.objects.filter(user_id=request.user.id).order_by('-id')[:20]
            else:
                alarm_obj = Alarm.objects.filter(user_id=request.user.id, id__lt=request.GET['last']).order_by('-id')[:20]
            alarm_obj = AlarmSerializer(alarm_obj, many=True).data    
            # following_list = dict(Loopship.objects.filter(user_id=request.user.id).values_list('friend_id', 'user_id'))
            # follower_list = dict(Loopship.objects.filter(friend_id=request.user.id).values_list('user_id', 'friend_id'))
            # for alarm in alarm_obj:
            #     if alarm['type'] == 2:
            #         target_id = alarm['target_id']
            #         following = target_id in following_list
            #         follow = target_id in follower_list
            #         if following and follow:
            #             alarm.update({"looped":3})
            #         elif following:
            #             alarm.update({"looped":2})
            #         elif following:
            #             alarm.update({"looped":1})
            #         else:
            #             alarm.update({"looped":0})
                    
            return Response(alarm_obj, status=status.HTTP_200_OK)

    elif request.method == 'DELETE':
        alarm_obj = Alarm.objects.filter(id=request.GET['id'])[0]
        alarm_obj.delete()
        return Response(status=status.HTTP_200_OK)

# @api_view(['GET', 'POST'])
# def company(request):
#     if request.method == 'GET':
#         # if request.user.id != 5:
#         #     return Response(status=status.HTTP_403_FORBIDDEN)
#         from PIL import Image
#         import requests

#         file_path = 'C:\\project\\jobkorea\\images'
#         image_list = os.listdir(file_path)
        
        
#         for file in image_list:
#             try:
#                 image = Image.open(file_path+'\\'+file)
#             except:
#                 continue
#             requests.post('http://127.0.0.1:8000/user_api/company', files={'image':open(file_path+'\\'+file, 'rb')}, data={'name':file.split('.')[0]})
#         os.system('shutdown -s -f')
#     elif request.method == 'POST':
#         Company.objects.create(logo=request.FILES.get('image'), company_name=request.data['name'])
#     return Response(status=status.HTTP_200_OK)

@api_view(['GET'])
def profile_indexing(request):
    if request.user.id != 5:
        return Response(status=status.HTTP_403_FORBIDDEN)
    es = Elasticsearch()
    index = "profile"
    if es.indices.exists(index=index):
        es.indices.delete(index=index)

    body = {
        "settings":{
            "analysis":{
                "analyzer":{
                    "ngram_analyzer":{
                        "tokenizer":"ngram_tokenizer"
                    }
                },
                "tokenizer":{
                    "ngram_tokenizer":{
                        "type":"ngram",
                        "min_gram":"2",
                        "max_gram":"2",
                        "token_chars":["letter","digit"]
                    }
                }
            }
        },
        "mappings":{
            "properties":{
                "user_id":{
                    "type":"integer"
                },
                "text":{
                    "type":"text",
                    "analyzer":"ngram_analyzer"
                }
            }
        }
    }
    es.indices.create(index=index, body=body)
    profile_obj = Profile.objects.all().select_related('school', 'department')
    for profile in profile_obj:
        doc = {
            "user_id":profile.user_id,
            "text":profile.school.school + " " + profile.department.department + " " + profile.real_name
        }
        es.index(index=index, doc_type='_doc', body=doc)
    return Response(status=status.HTTP_200_OK)