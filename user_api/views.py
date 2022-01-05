from django.shortcuts import redirect
from django.contrib.auth import authenticate
from django.contrib.auth.models import User
from django.contrib.auth.hashers import check_password
# for email check
from django.conf.global_settings import SECRET_KEY
from django.views import View

from project_api.serializers import ProjectSerializer
from .text import pwmessage

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

from django.conf.global_settings import SECRET_KEY

from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.authtoken.models import Token
from rest_framework import status

# from .department import DEPARTMENT
from .models import Profile, Activation, Company_Inform
from .serializers import ProfileSerializer, ProfileTagSerializer

from tag.models import Tag, Profile_Tag
from project_api.models import Project
from fcm.models import FcmToken

import jwt
import json
import time
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

@api_view(['POST', ])
def check_email(request):
    
    email_obj = request.data['email']
    password_obj = request.data['password']
    username_obj = email_obj
    try:
        user = User.objects.get(username=email_obj)
        try:
            Token.objects.get(user_id=user.id)
            return Response(status=status.HTTP_400_BAD_REQUEST)

        except Token.DoesNotExist:
            user.delete()
            
    except User.DoesNotExist:
        pass
    
    except:
        return Response(status=status.HTTP_400_BAD_REQUEST)

    try:    
        user = User.objects.create_user(
            username = username_obj,
            email = email_obj,
            password = password_obj,
            is_active = False)

    except IntegrityError:
        return Response("이미 있는 아이디 입니다.", status=status.HTTP_401_UNAUTHORIZED)        
            
    current_site = get_current_site(request)
    domain = current_site.domain
    uidb4 = urlsafe_base64_encode(force_bytes(user.id))
    token = jwt.encode({'id': user.id}, SECRET_KEY,algorithm='HS256').decode('utf-8')# ubuntu환경
    # token = jwt.encode({'id': user.id}, SECRET_KEY, algorithm='HS256')
    html_content = f'<h3>아래 링크를 클릭하시면 인증이 완료됩니다.</h3><br><a href=http://{domain}/user_api/activate/{uidb4}/{token}>http://{domain}/user_api/activate/{uidb4}/{token}.</a><br><br><h3>감사합니다.</h3>'
    main_title = 'LOOP US 이메일 인증'
    mail_to = user.email
    msg = EmailMultiAlternatives(main_title, "아래 링크를 클릭하세요", to=[mail_to])
    msg.attach_alternative(html_content, "text/html")
    msg.send()

    for i in range(36):
        time.sleep(5)
        user = User.objects.get(pk=user.id)

        if user.is_active:
            return Response(status=status.HTTP_200_OK)

    user.delete()
    return Response(status=status.HTTP_408_REQUEST_TIMEOUT)

class Activate(View):
    def get(self, request, uidb64, token):

        uid = force_text(urlsafe_base64_decode(uidb64))
        user = User.objects.get(pk=uid)
        user_dic = jwt.decode(token, algorithms='HS256')
        if user.id == user_dic['id']:
            user.is_active = True
            user.save()

            return redirect("https://w.namu.la/s/ff250ecf6b040d461d70a54825fa840816bd399369d4fbcc9e71fe21a028435757556a886cf579feff0c97d373cbe88619c0d2bce59f741e21f2668dffe7978bc834e9da9ef0c3609b4bc5b89476f166d8c98764bdc2047eaf910159f9387d8e510ce80dc6238b903ffaf01f2b30e052")

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
            user_obj = User.objects.create_user(username=request.data['username'],
                                                password=request.data['password'],
                                                email=request.data['email'],
                                                is_active=False)
        except IntegrityError:
            return Response("이미 있는 아이디 입니다.", status=status.HTTP_401_UNAUTHORIZED)

        Activation.objects.create(user_id = user_obj.id,
                                  corp_num = request.data['corp_num'],
                                  corp_name = request.data['corp_name'],
                                  email = request.data['email'],
                                  name = request.data['name'],
                                  tel_num = request.data['tel_num'])

        return Response("인증 대기중입니다.", status=status.HTTP_201_CREATED)

@api_view(['POST', ])
def signup(request):
    type = request.data['type']

    if type == 1:
        user_obj = User.objects.get(username=request.data['username'])
    else:
        user_obj = User.objects.get(username=request.data['email'])
    

    if user_obj.is_active:
        token = Token.objects.create(user_id=user_obj.id)

        try:
            profile_obj = Profile.objects.create(user_id = user_obj.id,
                                                 type = type,
                                                 real_name = request.data['real_name'],
                                                 profile_image = None,
                                                 department = request.data['department'])
        except:
            token.delete()
            return Response('Profile information is not invalid', status=status.HTTP_404_NOT_FOUND)
        for tag in request.data['tag']:
            try:
                tag_obj = Tag.objects.get(tag=tag)
                tag_obj.count = tag_obj.count + 1
                tag_obj.save()
            
            except Tag.DoesNotExist:
                tag_obj = Tag.objects.create(tag = tag)
            
            Profile_Tag.objects.create(profile = profile_obj, tag=tag_obj)

        if type == 1:
            corp = Activation.objects.get(user_id=user_obj.id)
            Company_Inform.objects.create(profile_id = profile_obj.id,
                                          corp_num = corp.corp_num,
                                          corp_name = corp.corp_name)
            corp.delete()

        return Response({'message':'singup success',
                         'token':str(token),
                         'user_id':token.user_id,
                         'isAuthoriztion':1})
    else:
        return Response({'message':'login failed',
                         'isAuthoriztion':0})


@api_view(['POST', ])
def login(request):
    user = authenticate(
        username=request.data['username'],
        password=request.data['password'],
    )
    if user is not None and user.is_active:
        token = Token.objects.get(user=user)
        user.last_login = timezone.now()
        user.save()
        
        try:
            token_obj = FcmToken.objects.get(user_id=user.id)
            if token_obj.token != request.data['fcm_token']:
                token_obj.token = request.data['fcm_token']
                token_obj.save()

        except FcmToken.DoesNotExist:
            FcmToken.objects.create(user_id=user.id,
                                    token=request.data['fcm_token'])

        return Response({'Token':token.key,
                         'user_id':str(token.user_id)}, status=status.HTTP_202_ACCEPTED)
    
    else:
        return Response("인증 만료 로그인 불가",status=status.HTTP_401_UNAUTHORIZED)

@api_view(['POST', ])
@permission_classes((IsAuthenticated,))
def new_password(request):
    user = request.user

    alphabet = ['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i', 'j', 'k', 'l', 'm', 'n', 'o', 'p', 'q', 'r', 's', 't', 'u', 'v', 'w', 'x', 'y', 'z']
    char = [ '!', '"', '#', '$', '%', '&', "'", '(', ')', '*', '+' , ',',  '-', '.', '/', ':', ';', '<', '=', '>', '?', '@', '[', ']', '^', '_', '`', '{', '|', '}', '~']
    new_password = ''

    for i in range(5):
        alpha = random.choice(alphabet)
        ch = random.choice(char)
        new_password = new_password + alpha + ch

    user.set_password(new_password)
    user.save()

    profile_obj = Profile.objects.get(user_id=user.id)
    real_name = profile_obj.real_name
    EmailMessage("새로운 비밀번호입니다.", pwmessage(real_name, new_password), to=[user.email]).send()

    return Response(status=status.HTTP_200_OK)

@api_view(['POST', ])
@permission_classes((IsAuthenticated,))
def change_password(request):
    user = request.user
    
    if check_password(request.data['origin_pw'], user.password):
        new_pw = request.data['new_pw']
        user.set_password(new_pw)
        user.save()
        return Response("pw is changed", status=status.HTTP_200_OK)
    else:
        return Response("origin_pw is not matched with data", status=status.HTTP_401_UNAUTHORIZED)

@api_view(['POST', ])
@permission_classes((IsAuthenticated,))
def resign(request):  
    user = request.user
    user_obj = User.objects.get(id=user.id)
    user_obj.delete()
    return Response("resign from loop", status=status.HTTP_200_OK)
    
@api_view(['POST', ])
@permission_classes((IsAuthenticated,))
def update_profile(request):
    profile = Profile.objects.get(user_id=request.user.id)
    profile.department = request.data['department']
    if type(request.data['image']) == str:
        pass
    
    else:
        profile.profile_image = request.FILES.get('image')
    
    profile.save()

    tag_list = eval(request.data['tag'])

    old_tag = Profile_Tag.objects.filter(profile_id=profile.id)
    old_sz = ProfileTagSerializer(old_tag, many=True)
    old_tag_list = []

    for tag in old_sz.data:
        old_tag_list.append(tag['tag'])

        if tag['tag'] not in tag_list:
            Profile_Tag.objects.get(tag_id=tag['tag_id'], profile=profile).delete()
            tag_obj = Tag.objects.get(id=tag['tag_id'])
            tag_obj.count = tag_obj.count - 1
            if tag_obj.count == 0:
                tag_obj.delete()
            else:    
                tag_obj.save()
    
    for tag in tag_list:
        if tag in old_tag_list:
            continue
        else:
            try:
                tag_obj = Tag.objects.get(tag=tag)
                tag_obj.count = tag_obj.count + 1
                tag_obj.save()

            except Tag.DoesNotExist:
                tag_obj = Tag.objects.create(tag = tag)

            Profile_Tag.objects.create(tag = tag_obj, profile = profile)
    
    return Response(ProfileSerializer(profile).data, status=status.HTTP_200_OK)

@api_view(['GET', ])
@permission_classes((IsAuthenticated,))
def profile_load(request, idx):
    return_dict = {}

    profile = Profile.objects.get(user_id=idx)
    project_obj = Project.objects.filter(user_id=idx)

    project_sz = ProjectSerializer(project_obj, many=True)
    profile_sz = ProfileSerializer(profile)

    return_dict.update(profile_sz.data)
    return_dict.update({"project":project_sz.data})

    if str(request.user.id) == idx:
        return_dict.update({'is_user':1})
    else:
        return_dict.update({'is_user':0})
    
    return Response(return_dict, status=status.HTTP_200_OK)