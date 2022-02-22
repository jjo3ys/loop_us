from django.shortcuts import redirect
from django.contrib.auth import authenticate
from django.contrib.auth.models import User
from django.contrib.auth.hashers import check_password
# for email check
from django.conf.global_settings import SECRET_KEY
from django.views import View
from django.conf import settings



from django.contrib.sites.shortcuts import get_current_site
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

from fcm.push_fcm import report_alarm, topic_alarm

# from .department import DEPARTMENT
from .models import Profile, Activation, Company_Inform, Banlist, Report, Alarm
from .serializers import AlarmSerializer, BanlistSerializer, ProfileSerializer
from .department import DEPARTMENT, R_DEPARTMENT
from .university import UNIVERSITY
from .text import pwmessage

from search.models import InterestTag
from tag.models import Project_Tag, Question_Tag, Tag, Profile_Tag
from project_api.models import Project
from project_api.serializers import ProjectSerializer
from post_api.models import ContentsImage, Post
from question_api.models import Question
from loop.models import Loopship
from fcm.models import FcmToken
from chat.models import Room, Msg

import jwt
import json
import time
import datetime
import random
import requests

headers = {
    'Accpet':'application/json',
    'Authorization':'frbSEAcXD+a6UEOUq1lkWcWmFoDku20SZvLeO++pP9e5yQo5GIqTkbVbctqafewScJuzLLcTW/l4d/Lw/wjOig==',
    'Content-Type': 'application/json',
}

params = (
    ('serviceKey', 'frbSEAcXD+a6UEOUq1lkWcWmFoDku20SZvLeO++pP9e5yQo5GIqTkbVbctqafewScJuzLLcTW/l4d/Lw/wjOig=='),
)
def delete_tag(tag_obj):
    for tag in tag_obj:
        tag.tag.count = tag.tag.count-1
        if tag.tag.count == 0:
            tag.tag.delete()
        else:
            tag.tag.save()


def check_email(user, type):           
    uidb4 = urlsafe_base64_encode(force_bytes(user.id))
    # token = jwt.encode({'id': user.id}, SECRET_KEY,algorithm='HS256').decode('utf-8')# ubuntu환경
    token = jwt.encode({'id': user.id}, SECRET_KEY, algorithm='HS256')
    html_content = f'<h3>아래 링크를 클릭하시면 인증이 완료됩니다.</h3><br><a href="http://3.35.253.151:8000/user_api/activate/{uidb4}/{token}">이메일 인증 링크</a><br><br><h3>감사합니다.</h3>'
    main_title = 'LOOP US 이메일 인증'
    mail_to = user.email
    msg = EmailMultiAlternatives(main_title, "아래 링크를 클릭하여 인증을 완료해 주세요.", to=[mail_to])
    msg.attach_alternative(html_content, "text/html")
    msg.send()

    for i in range(90):
        time.sleep(2)
        user = User.objects.get(pk=user.id)

        if user.is_active:
            return Response(status=status.HTTP_200_OK)

    if type == 'create':
        user.delete()

    elif type == 'find':
        user.is_active = True
        user.save()

    return Response(status=status.HTTP_408_REQUEST_TIMEOUT)

@api_view(['POST', ])
def create_user(request):
    
    email_obj = request.data['email']
    password_obj = request.data['password']
    username_obj = email_obj
    try:
        user = User.objects.get(username=email_obj)
        try:
            Token.objects.get(user_id=user.id)
            return Response("이미 있는 아이디 입니다.", status=status.HTTP_400_BAD_REQUEST)

        except Token.DoesNotExist:
            user.delete()
            
    except User.DoesNotExist:
        pass
    
    except:
        return Response(status=status.HTTP_400_BAD_REQUEST)

    try:    
        user = User.objects.create_user(username = username_obj,
                                        email = email_obj,
                                        password = password_obj,
                                        is_active = False)

    except IntegrityError:
        return Response("이미 있는 아이디 입니다.", status=status.HTTP_401_UNAUTHORIZED)        
    check_email(user, 'create')
    return Response(status=status.HTTP_200_OK)
@api_view(['GET', ])
def activate(request, uidb64, token):
    uid = force_text(urlsafe_base64_decode(uidb64))
    user = User.objects.get(pk=uid)
    user_dic = jwt.decode(token, algorithms='HS256')
    if user.id == user_dic['id']:
        user.is_active = True
        user.save()
        
        return redirect("https://loopusimage.s3.ap-northeast-2.amazonaws.com/static/email_authentication_image.png")

    return Response({'message': 'email check fail...'})
    
class Activate(View):
    def get(self, request, uidb64, token):

        uid = force_text(urlsafe_base64_decode(uidb64))
        user = User.objects.get(pk=uid)
        user_dic = jwt.decode(token, algorithms='HS256')
        if user.id == user_dic['id']:
            user.is_active = True
            user.save()
            
            return redirect("https://loopusimage.s3.ap-northeast-2.amazonaws.com/static/email_authentication_image.png")

        return Response({'message': 'email check fail...'})

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

        return Response("인증 대기중입니다.", status=status.HTTP_201_CREATED)

@api_view(['POST'])
def signup(request):
    type = request.data['type']

    if type == 1:
        user = User.objects.get(username=request.data['username'])
    else:
        user = User.objects.get(username=request.data['email'])
    

    if user.is_active:
        token = Token.objects.create(user_id=user.id)

        try:
            department_id = R_DEPARTMENT[request.data['department']]
            profile_obj = Profile.objects.create(user_id = user.id,
                                                type = type,
                                                real_name = request.data['real_name'],
                                                profile_image = None,
                                                department = department_id)
        except:
            token.delete()
            return Response('Profile information is not invalid', status=status.HTTP_404_NOT_FOUND)
        tag_list = {}
        for tag in request.data['tag']:
            try:
                tag_obj = Tag.objects.get(tag=tag)
                tag_obj.count = tag_obj.count + 1
                tag_obj.save()
            
            except Tag.DoesNotExist:
                tag_obj = Tag.objects.create(tag = tag)

            tag_list[str(tag_obj.id)] = {'count':1, 'date':str(datetime.date.today()), 'id':tag_obj.id}
            Profile_Tag.objects.create(profile = profile_obj, tag=tag_obj)

        InterestTag.objects.create(user_id=user.id, tag_list=tag_list)
        if type == 1:
            corp = Activation.objects.get(user_id=user.id)
            Company_Inform.objects.create(profile_id = profile_obj.id,
                                        corp_num = corp.corp_num,
                                        corp_name = corp.corp_name)
            corp.delete()

        return Response({'token':token.key, 'user_id':user.id},status=status.HTTP_201_CREATED)
    else:
        return Response(status=status.HTTP_401_UNAUTHORIZED)

@api_view(['POST'])
def login(request):
    user = authenticate(
    username=request.data['username'],
    password=request.data['password'],
    )
    if user is not None and user.is_active:
        token_obj = Token.objects.get(user=user)
        user.last_login = timezone.now()
        user.save()
        
        try:
            fcm_obj = FcmToken.objects.get(user_id=user.id)
            if fcm_obj.token != request.data['fcm_token']:
                fcm_obj.token = request.data['fcm_token']
                fcm_obj.save()

        except FcmToken.DoesNotExist:
            FcmToken.objects.create(user_id=user.id,
                                    token=request.data['fcm_token'])

        return Response({'token':token_obj.key,
                        'user_id':str(token_obj.user_id)}, status=status.HTTP_202_ACCEPTED)
    
    else:
        return Response("인증 만료 로그인 불가",status=status.HTTP_401_UNAUTHORIZED)

@api_view(['POST'])
@permission_classes((IsAuthenticated,))
def logout(request):
    user = request.user
    try:
        fcm_obj = FcmToken.objects.get(user_id=user.id)
        fcm_obj.delete()
    except:
        pass
    return Response("Successed log out", status=status.HTTP_200_OK)
    
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
            user = User.objects.get(email=request.data['email'])
            user.set_password(request.data['password'])
            user.save()
            return Response(status=status.HTTP_200_OK)

    elif request.method =='POST':
        user = User.objects.get(email=request.data['email'])

        user.is_active = False
        user.save()
        check_email(user, 'find')
        return Response(status=status.HTTP_200_OK)
    
   

@api_view(['POST', ])
@permission_classes((IsAuthenticated,))
def resign(request):   
    if check_password(request.data['password'], request.user.password):
        user = request.user
        profile_obj = Profile.objects.get(user_id=user.id)
        profile_obj.profile_image.delete(save=False)
        try:
            intereset_list = InterestTag.objects.get(user_id=user.id)
            intereset_list.delete()
        except:
            pass

        for project in Project.objects.filter(user_id=user.id):
            project.pj_thumbnail.delete(save=False)
            for post in Post.objects.filter(project_id=project.id):
                for image in ContentsImage.objects.filter(post_id=post.id):
                    image.image.delete(save=False)

        tag_obj = Profile_Tag.objects.filter(profile_id=profile_obj.id)
        delete_tag(tag_obj)
        tag_obj = Project_Tag.objects.filter(project__in=Project.objects.filter(user_id=user.id))
        delete_tag(tag_obj)
        tag_obj = Question_Tag.objects.filter(question__in=Question.objects.filter(user_id=user.id))
        delete_tag(tag_obj)
        
        user = User.objects.get(id=user.id)
        user.delete()
        return Response("resign from loop", status=status.HTTP_200_OK)

    else:
        return Response(status=status.HTTP_401_UNAUTHORIZED)   
    
    
@api_view(['PUT', 'GET'])
@permission_classes((IsAuthenticated,))
def profile(request):
    if request.method == 'PUT':
        profile_obj = Profile.objects.get(user_id=request.user.id)
        type = request.GET['type']

        if type == 'image':
            profile_obj.profile_image.delete(save=False)
            profile_obj.profile_image = request.FILES.get('image')
        
        elif type == 'department':
            profile_obj.department = R_DEPARTMENT[request.data['department']]
        
        elif type == 'tag':
            interest_list = InterestTag.objects.get_or_create(user_id=request.user.id)[0]
            tag_obj = Profile_Tag.objects.filter(profile_id=profile_obj.id)
            for tag in tag_obj:
                try:
                    interest_list.tag_list[str(tag.tag.id)]['count'] -= 1
                    if interest_list.tag_list[str(tag.tag.id)]['count'] == 0:
                        del interest_list.tag_list[str(tag.tag.id)]
                except KeyError:
                    pass

                tag.delete()
                tag.tag.count = tag.tag.count-1
                if tag.tag.count == 0:
                    tag.tag.delete()
                tag.tag.save()

            tag_list = eval(request.data['tag'])      
            for tag in tag_list:
                tag_obj, valid = Tag.objects.get_or_create(tag=tag)
                Profile_Tag.objects.create(tag = tag_obj, profile_id = profile_obj.id)
                try:
                    interest_list.tag_list[str(tag_obj.id)]['count'] += 1
                    interest_list.tag_list[str(tag_obj.id)]['date'] = str(datetime.date.today())
                except KeyError:
                    interest_list.tag_list[str(tag_obj.id)] = {'count':1, 'date':str(datetime.date.today()), 'id':tag_obj.id}

                if not valid:
                    tag_obj.count = tag_obj.count+1
                    tag_obj.save()         
            interest_list.save()

        profile_obj.save()
        return Response(ProfileSerializer(profile_obj).data, status=status.HTTP_200_OK)
    
    if request.method == 'GET':
        idx = request.GET['id']
        profile = ProfileSerializer(Profile.objects.get(user_id=idx)).data
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
            # interest_tag = InterestTag.objects.get_or_create(user_id=request.user.id)[0]
            # for tag in profile['profile_tag']:
            #     try:
            #         interest_tag.tag_list[str(tag['tag_id'])]['count'] += 1
            #         interest_tag.tag_list[str(tag['tag_id'])]['date'] = str(datetime.date.today())
            #     except KeyError:
            #          interest_list.tag_list[str(tag['tag_id'])] = {'count':1, 'date':str(datetime.date.today()), 'id':tag['tag_id']}

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

        return Response(profile, status=status.HTTP_200_OK)

@api_view(['GET', ])
@permission_classes((IsAuthenticated,))
def project(request):
    idx = request.GET['id']
    project_obj = list(Project.objects.filter(user_id=idx))
    project_obj.reverse()
    project_obj = ProjectSerializer(project_obj, many=True).data
    if request.user.id == int(idx):
        for p in project_obj:
            p.update({"is_user":1})
    else:
        for p in project_obj:
            p.update({"is_user":0})

    return Response(project_obj, status=status.HTTP_200_OK)

@api_view(['GET', ])
def department_list(request):
    return Response(DEPARTMENT, status=status.HTTP_200_OK)

@api_view(['GET', ])
def university_list(request):
    return Response(UNIVERSITY, status=status.HTTP_200_OK)

@api_view(['POST'])
@permission_classes((IsAuthenticated,))
def report_profile(request):
    Report.objects.create(user_id=request.user.id, type=True, target_id=request.data['id'], reason=request.data['reason'])
    count = Report.objects.filter(type=True, target_id=request.data['id']).count()
    if count >= 3:
        report_alarm(count, True, request.data['id'], request.data['reason'])
    return Response(status=status.HTTP_200_OK)

@api_view(['POST', 'DELETE', 'GET'])
@permission_classes((IsAuthenticated,))
def ban(request):
    if request.method == 'POST':
        banlist_obj, valid = Banlist.objects.get_or_create(user_id=request.user.id)
        if not valid:
            ban_list = banlist_obj.banlist
            banlist_obj.banlist = ban_list.append(int(request.GET['id']))      
        else:
            banlist_obj.banlist=[int(request.GET['id'])]
           
        banlist_obj.save()
        try:
            Loopship.objects.get(user_id=request.user.id, friend_id=request.GET['id']).delete()
        except:
            pass

        try:
            Loopship.objects.get(user_id=request.GET['id'], friend_id=request.user.id).delete()
        except:
            pass

        return Response(status=status.HTTP_200_OK)
    
    elif request.method == 'DELETE':
        banlist_obj = Banlist.objects.get(user_id=request.user.id)
        banlist_obj.banlist.remove(int(request.GET['id']))
        banlist_obj.save()
        return Response(status=status.HTTP_200_OK)

    elif request.method == 'GET':
        try:
            banlist_obj = Banlist.objects.get(user_id=request.user.id)  
        except:
            return Response(status=status.HTTP_404_NOT_FOUND)
        return Response(BanlistSerializer(banlist_obj).data, status=status.HTTP_200_OK)

@api_view(['GET', 'DELETE'])
@permission_classes((IsAuthenticated,))
def alarm(request):
    if request.method == 'GET':
        if request.GET['type'] == 'follow':
            if request.GET['last'] == '0':
                alarm_obj = list(Alarm.objects.filter(user_id=request.user.id, type=2))[-10:]
                
            else:
                alarm_obj = list(Alarm.objects.filter(user_id=request.user.id, id__lt=request.GET['last'], type=2))[-10:]
            
            for alarm in alarm_obj:
                if not alarm.is_read:
                    alarm.is_read = True
                    alarm.save()
            alarm_obj = AlarmSerializer(reversed(list(alarm_obj)), many=True).data
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
        else:            
            if request.GET['last'] == '0':
                alarm_obj = list(Alarm.objects.filter(user_id=request.user.id).exclude(type=2))[-10:]

            else:
                alarm_obj = list(Alarm.objects.filter(user_id=request.user.id, id__lt=request.GET['last']).exclude(type=2))[-10:]

            for alarm in alarm_obj:
                if not alarm.is_read:
                    alarm.is_read = True
                    alarm.save()
                    
            return Response(AlarmSerializer(reversed(list(alarm_obj)), many=True).data, status=status.HTTP_200_OK)

    elif request.method == 'DELETE':
        alarm_obj = Alarm.objects.get(id=request.GET['id'])
        alarm_obj.delete()
        return Response(status=status.HTTP_200_OK)

# @api_view(['GET', ])
# def noti(request):
#     topic_alarm('promotion', '프로모션토픽')
#     return Response(status=status.HTTP_200_OK)