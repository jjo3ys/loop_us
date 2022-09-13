import os
from django.shortcuts import redirect
from django.contrib.auth import authenticate
from django.contrib.auth.models import User
from django.contrib.auth.hashers import check_password
from django.core.paginator import Paginator
# for email check
from django.conf.global_settings import SECRET_KEY

from django.core.mail import EmailMessage, EmailMultiAlternatives
from django.utils import timezone
from django.utils.http import (
    urlsafe_base64_encode,
    urlsafe_base64_decode,
)
from django.utils.encoding import (
    force_bytes,
    force_text
)
from django.db.utils import IntegrityError

from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.authtoken.models import Token
from rest_framework import status

from fcm.push_fcm import certify_fcm, report_alarm
from post_api.serializers import MainloadSerializer

# from .department import DEPARTMENT
from .models import Profile, Activation, Company_Inform, Banlist, Report, Alarm, Company
from .serializers import AlarmSerializer, BanlistSerializer, ProfileSerializer

from search.models import Get_log, InterestTag
from tag.models import Post_Tag
from project_api.models import Project, ProjectUser
from project_api.serializers import ProjectUserSerializer
from post_api.models import BookMark, Like, PostImage, Post
from loop.models import Loopship
# from fcm.models import FcmToken
from chat.models import Room, Msg

from elasticsearch import Elasticsearch

import jwt
import json
import redis
import datetime
import requests
import platform

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
    r = client.get(email)
    if not r:
        pass
    else:
        client.delete(email)
    if platform.system() == 'Linux':
        token = jwt.encode({'id': email}, SECRET_KEY, algorithm='HS256').decode('utf-8')# ubuntu환경
    else:
        token = jwt.encode({'id': email}, SECRET_KEY, algorithm='HS256')
    html_content = f'<h3>아래 링크를 클릭하시면 인증이 완료됩니다.</h3><br>\
                     <a href="http://3.35.253.151:8000/user_api/activate/{token}">이메일 인증 링크</a><br><br>\
                     <h3>감사합니다.</h3>'

    main_title = 'LOOP US 이메일 인증'
    mail_to = email
    msg = EmailMultiAlternatives(main_title, "아래 링크를 클릭하여 인증을 완료해 주세요.", to=[mail_to])
    msg.attach_alternative(html_content, "text/html")
    msg.send()
    client.set(email.replace('@', ''), 0, datetime.timedelta(seconds=180))

@api_view(['POST'])
def create_user(request):
    if User.objects.filter(username=request.data['email']).exists():
        return Response(status=status.HTTP_400_BAD_REQUEST)
    send_msg(request.data['email'])
    return Response(status=status.HTTP_200_OK)

@api_view(['GET', ])
def activate(request, token):
    try:
        user_dic = jwt.decode(token, algorithms='HS256')
        email = user_dic['id']
        email = email.replace('@', '')
        r =  client.get(email)
        if int(r) == 0:
            client.delete(email)
            user = User.objects.filter(username=user_dic['id'])
            if user.exists():
                user = user[0]
                user.is_active = True
                user.save()
            else:
                pass
            certify_fcm(email)
            return redirect("https://loopusimage.s3.ap-northeast-2.amazonaws.com/static/email_authentification_success.png")
    except:
        return redirect("https://loopusimage.s3.ap-northeast-2.amazonaws.com/static/email_authentification_fail.png")

# @api_view(['POST', ])
# def create_user(request):
#     try:
#         user = User.objects.filter(username=request.data['email'])[0]
#         if user.is_active:
#             if Token.objects.filter(user_id=user.id).exists():            
#                 return Response("이미 있는 아이디 입니다.", status=status.HTTP_401_BAD_REQUEST)
#         else:
#             user.delete()#유저 정보는 있지만 토큰이 없을 때
            
#     except IndexError:
#         pass
    
#     except:
#         return Response(status=status.HTTP_400_BAD_REQUEST)
    
#     user = User.objects.create_user(username = request.data['email'],
#                                     email = request.data['email'],
#                                     password = 'loopus',
#                                     is_active = False)

#     uidb4 = urlsafe_base64_encode(force_bytes(user.id))
#     if platform.system() == 'Linux':
#         token = jwt.encode({'id': user.id}, SECRET_KEY,algorithm='HS256').decode('utf-8')# ubuntu환경
#     else:
#         token = jwt.encode({'id': user.id}, SECRET_KEY, algorithm='HS256')

#     html_content = f'<h3>아래 링크를 클릭하시면 인증이 완료됩니다.</h3><br>\
#                      <a href="http://3.35.253.151:8000/user_api/activate/{uidb4}/{token}">이메일 인증 링크</a><br><br>\
#                      <h3>감사합니다.</h3>'

#     main_title = 'LOOP US 이메일 인증'
#     mail_to = user.email
#     msg = EmailMultiAlternatives(main_title, "아래 링크를 클릭하여 인증을 완료해 주세요.", to=[mail_to])
#     msg.attach_alternative(html_content, "text/html")
#     msg.send()
#     return Response(status=status.HTTP_200_OK)

# @api_view(['GET', ])
# def activate(request, uidb64, token):
#     try:
#         uid = force_text(urlsafe_base64_decode(uidb64))
#         user = User.objects.filter(pk=uid)[0]
#         user_dic = jwt.decode(token, algorithms='HS256')
#         if user.id == user_dic['id']:
#             user.is_active = True
#             user.save()
            
#             return redirect("https://loopusimage.s3.ap-northeast-2.amazonaws.com/static/email_authentification_success.png")
#         else:
#             return redirect("https://loopusimage.s3.ap-northeast-2.amazonaws.com/static/email_authentification_fail.png")

#     except:
#         return redirect("https://loopusimage.s3.ap-northeast-2.amazonaws.com/static/email_authentification_fail.png")

# @api_view(['GET'])
# def check_valid(request):    
#     user = User.objects.filter(username=request.GET['email'])
#     if user.exists() and user[0].is_active:
#         return Response(status=status.HTTP_200_OK)
    
#     else:
#         return Response(status=status.HTTP_401_UNAUTHORIZED)

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
    else:
        loop_list = []
        dep_loop = Profile.objects.filter(department_id=request.data['department']).exclude(user_id=user.id)
        for looper in dep_loop:
            loop_list.append(Loopship(user_id=user.id, friend_id=looper.user_id))
            loop_list.append(Loopship(user_id=looper.user_id, friend_id=user.id))
        Loopship.objects.bulk_create(loop_list)
    # InterestTag.objects.create(user_id=user.id, tag_list={})
    return Response({'token':token.key, 'user_id':str(user.id)},status=status.HTTP_200_OK)

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
        
        # try:
        #     fcm_obj = FcmToken.objects.filter(user_id=user.id)[0]
        #     if fcm_obj.token != request.data['fcm_token']:
        #         try:
        #             logout_push(fcm_obj.token)
        #         except:
        #             pass
                
        #         fcm_obj.token = request.data['fcm_token']
        #         fcm_obj.save()

        # except IndexError:
        #     FcmToken.objects.create(user_id=user.id,
        #                             token=request.data['fcm_token'])

        return Response({'token':token_obj.key,
                        'user_id':str(token_obj.user_id)}, status=status.HTTP_202_ACCEPTED)
    
    else:
        return Response("인증 만료 로그인 불가",status=status.HTTP_401_UNAUTHORIZED)
        
# @api_view(['POST'])
# @permission_classes((IsAuthenticated,))
# def logout(request):
#     user = request.user
#     try:
#         fcm_obj = FcmToken.objects.filter(user_id=user.id)[0]
#         fcm_obj.delete()
#     except:
#         pass
#     return Response("Successed log out", status=status.HTTP_200_OK)

# @api_view(['POST'])
# @permission_classes((IsAuthenticated,))
# def check_token(request):
#     try:
#         if request.data['fcm_token'] != FcmToken.objects.filter(user_id=request.user.id)[0].token:
#             return Response(status=status.HTTP_401_UNAUTHORIZED)
#         else:
#             return Response(status=status.HTTP_200_OK)
#     except:
#         return Response(status=status.HTTP_401_UNAUTHORIZED)
    
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
    if check_password(request.data['password'], request.user.password):
        user = request.user
        profile_obj = Profile.objects.filter(user_id=user.id).select_related('department').select_related('school')[0]
        profile_obj.profile_image.delete(save=False)
        message = EmailMessage('{}님 탈퇴 사유'.format(profile_obj.real_name), '{} {} \n 사유:{}'.format(profile_obj.school.school, profile_obj.department.department, request.data['reason']), to=['loopus@loopus.co.kr'])
        try:
            message.send()
        except:
            return Response(status=status.HTTP_406_NOT_ACCEPTABLE)

        try:
            intereset_list = InterestTag.objects.filter(user_id=user.id)[0]
            intereset_list.delete()
        except:
            pass

        for project in Project.objects.filter(user_id=user.id):
            for post in Post.objects.filter(project_id=project.id):
                for image in PostImage.objects.filter(post_id=post.id):
                    image.image.delete(save=False)

        tag_obj = Post_Tag.objects.filter(post__in=Post.objects.filter(user_id=user.id))
        delete_tag(tag_obj)
        es = Elasticsearch()
        es.delete_by_query(index='profile', doc_type='_doc', body={'query':{'match':{"user_id":{"query":request.user.id}}}})
        user = User.objects.filter(id=user.id)[0]
        user.delete()
        return Response("resign from loop", status=status.HTTP_200_OK)

    else:
        return Response(status=status.HTTP_401_UNAUTHORIZED)   

@api_view(['POST', ])
@permission_classes((IsAuthenticated,))
def ask(request):
    message = EmailMessage('{}님 문의'.format(request.data['real_name']), '이메일:{} \n 문의내용:{} \n 기기:{} \n OS버젼:{} \n 빌드번호:{} \n 유저id:{}'.format(request.data['email'],
                                                                                                                                                         request.data['content'],
                                                                                                                                                         request.data['device'],
                                                                                                                                                         request.data['os'],
                                                                                                                                                         request.data['app_ver'],
                                                                                                                                                         request.data['id']), to=['loopus@loopus.co.kr'])
    try:
        message.send()
        return Response(status=status.HTTP_200_OK)
    except:
        return Response(status=status.HTTP_406_NOT_ACCEPTABLE)
    
@api_view(['PUT', 'GET'])
@permission_classes((IsAuthenticated,))
def profile(request):
    if request.method == 'PUT':
        profile_obj = Profile.objects.filter(user_id=request.user.id)[0]
        type = request.GET['type']

        if type == 'image':
            profile_obj.profile_image.delete(save=False)
            profile_obj.profile_image = request.FILES.get('image')
        
        elif type == 'department':
            profile_obj.department = request.data['department']

        profile_obj.save()
        return Response(ProfileSerializer(profile_obj).data, status=status.HTTP_200_OK)
    
    elif request.method == 'GET':
        idx = request.GET['id']
        try:
            profile_obj = Profile.objects.filter(user_id=idx)[0]
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
            # Get_log.objects.create(user_id=request.user.id, target_id=idx, type=1)
            profile_obj.view_count += 1
            profile_obj.save()

            profile.update({'is_user':0})
            if Banlist.objects.filter(user_id=request.user.id, banlist__contains=int(idx)).exists():
                profile.update({'is_banned':1})
            elif Banlist.objects.filter(user_id=idx, banlist__contains=request.user.id).exists():
                profile.update({'is_banned':2})
            else:
                profile.update({'is_banned':0})

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

@api_view(['GET', ])
@permission_classes((IsAuthenticated,))
def project(request):
    idx = request.GET['id']
    try:
        project_obj = ProjectUser.objects.filter(user_id=idx).select_related('project')
    except:
        return Response(status=status.HTTP_404_NOT_FOUND)
    project_obj = ProjectUserSerializer(project_obj, many=True).data

    sum_post = Post.objects.filter(user_id=idx).count()

    if sum_post != 0:
        for project in project_obj:
            project.update({'ratio':round(project['post_count']/sum_post, 2)})
    else:
        for project in project_obj:
            project.update({'ratio':0})

    return Response(project_obj, status=status.HTTP_200_OK)

@api_view(['GET', ])
@permission_classes((IsAuthenticated,))
def posting(request):
    idx = int(request.GET['id'])
    if request.GET['type'] == 'career':
        post_obj = Post.objects.filter(project_id=idx).order_by('-id')
    elif request.GET['type'] == 'all':
        post_obj = Post.objects.filter(user_id=idx).order_by('-id')

    post_obj = Paginator(post_obj, 20)
    if post_obj.num_pages < int(request.GET['page']):
        return Response(status=status.HTTP_204_NO_CONTENT)

    post_obj = MainloadSerializer(post_obj.get_page(request.GET['page']), many=True, read_only=True).data
    for post in post_obj:
        exists = Like.objects.filter(post_id=post['id'], user_id=request.user.id).exists()
        if exists:
            post.update({"is_liked":1})
        else:
            post.update({"is_liked":0})
        
        exists = BookMark.objects.filter(user_id=request.user.id, post_id=post['id']).exists()
        if exists:
            post.update({"is_marked":1})
        else:
            post.update({"is_marked":0})

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
        if request.GET['type'] == 'follow':
            if request.GET['last'] == '0':
                alarm_obj = Alarm.objects.filter(user_id=request.user.id, type=2).order_by('-id')[:10]               
            else:
                alarm_obj = Alarm.objects.filter(user_id=request.user.id, id__lt=request.GET['last'], type=2).order_by('-id')[:10]
            
            alarm_obj = AlarmSerializer(alarm_obj, many=True).data
            for alarm in alarm_obj:
                follow = Loopship.objects.filter(user_id=request.user.id, friend_id=alarm['target_id']).exists()
                following = Loopship.objects.filter(user_id=alarm['target_id'], friend_id=request.user.id).exists()
                if follow and following:
                    alarm.update({"looped":3})
                elif follow:
                    alarm.update({"looped":2})#내가 알람 보낸 사람을 follow
                elif following:
                    alarm.update({"looped":1})#알람 보낸 사람이 나를 follow
                else:
                    alarm.update({"looped":0})

            return Response(alarm_obj, status=status.HTTP_200_OK)

        elif request.GET['type'] == 'else':            
            if request.GET['last'] == '0':
                alarm_obj = Alarm.objects.filter(user_id=request.user.id).exclude(type=2).order_by('-id')[:10]
            else:
                alarm_obj = Alarm.objects.filter(user_id=request.user.id, id__lt=request.GET['last']).exclude(type=2).order_by('-id')[:10]
                    
            return Response(AlarmSerializer(alarm_obj, many=True).data, status=status.HTTP_200_OK)

        elif request.GET['type'] == 'read':
            alarm_obj = Alarm.objects.filter(target_id=request.GET['id'], type=request.GET['type_id'], alarm_from_id=request.GET['sender_id'])[0]
            alarm_obj.is_read = True
            alarm_obj.save()

            return Response(status=status.HTTP_200_OK)

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
    profile_obj = Profile.objects.all().select_related('school').select_related('department')
    for profile in profile_obj:
        doc = {
            "user_id":profile.user_id,
            "text":profile.school.school + " " + profile.department.department + " " + profile.real_name
        }
        es.index(index=index, doc_type='_doc', body=doc)
    return Response(status=status.HTTP_200_OK)