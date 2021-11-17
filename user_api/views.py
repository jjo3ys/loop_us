from django.http import request
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate
from django.contrib.auth.models import User
# for email check
from django.conf.global_settings import SECRET_KEY
from django.views import View
from .text import message
from django.contrib.sites.shortcuts import get_current_site
from django.core.mail import EmailMessage
from django.utils.http import (
    urlsafe_base64_encode,
    urlsafe_base64_decode,
)
from django.utils.encoding import (
    force_bytes,
    force_text
)
from django.conf.global_settings import SECRET_KEY

from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.authtoken.models import Token
from rest_framework import status

# from .department import DEPARTMENT
from .models import Profile
from .serializers import ProfileSerializer, ProfileTagSerializer #, ProfileSerializer, UserSerializer

from tag.models import Tag, Profile_Tag

import jwt
import time

@api_view(['POST', ])
def check_email(request):
    
    email_obj = request.data['email']
    password_obj = request.data['password']
    username_obj = email_obj

    user = User.objects.create_user(
        username = username_obj,
        email = email_obj,
        password = password_obj,
        is_active = False
    )

    current_site = get_current_site(request)
    domain = current_site.domain
    uidb4 = urlsafe_base64_encode(force_bytes(user.id))
    # token = jwt.encode({'id': user.id}, SECRET_KEY,algorithm='HS256').decode('utf-8')# ubuntu환경
    token = jwt.encode({'id': user.id}, SECRET_KEY, algorithm='HS256')
    message_data = message(domain, uidb4, token)

    main_title = '이메일 인증을 완료해주세요.'
    mail_to = email_obj
    EmailMessage(main_title, message_data, to=[mail_to]).send()

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
def signup(request):

    user_obj = User.objects.get(username=request.data['email'])

    if user_obj.is_active:
        token = Token.objects.create(user=user_obj)

        try:
            profile_obj = Profile.objects.create(user = user_obj,
                                                 type = request.data['type'],
                                                 real_name = request.data['real_name'],
                                                 class_num = request.data['class_num'],
                                                 profile_image = request.data['image'])
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
    if user is not None:
        token = Token.objects.get(user=user)

        return Response({'Token':token.key,
                         'user_id':str(token.user_id)})
    
    else:
        return Response(status=status.HTTP_401_UNAUTHORIZED)

@api_view(['POST', ])
@permission_classes((IsAuthenticated,))
def update_profile(request):
    profile = Profile.objects.get(user_id=request.user.id)

    profile.type = request.data['type']
    profile.real_name = request.data['real_name']
    profile.class_num = request.data['class_num']
    if type(request.data['image']) == str:
        pass
    
    else:
        profile.profile_image = request.data['image']
    
    profile.save()

    old_tag = Profile_Tag.objects.filter(profile_id=profile.id)
    old_sz = ProfileTagSerializer(old_tag, many=True)
    old_tag_list = []

    for tag in old_sz.data:
        old_tag_list.append(tag['tag'])

        if tag['tag'] not in request.data['tag']:
            Profile_Tag.objects.get(tag_id=tag['tag_id'], project=profile).delete()
            tag_obj = Tag.objects.get(id=tag['tag_id'])
            tag_obj.count = tag_obj.count - 1
            if tag_obj.count == 0:
                tag_obj.delete()
            else:    
                tag_obj.save()
    
    for tag in request.data['tag']:
        if tag in old_tag_list:
            continue
        else:
            try:
                tag_obj = Tag.objects.get(tag=tag)
                tag_obj.count = tag_obj.count + 1
                tag_obj.save()

            except Tag.DoesNotExist:
                tag_obj = Tag.objects.create(tag = tag)

            Profile_Tag.objects.create(tag = tag_obj, project = profile)

    return Response("ok", status=status.HTTP_200_OK)

@api_view(['GET', ])
@permission_classes((IsAuthenticated,))
def profile_load(request, idx):
    user = Profile.objects.get(user_id=request.user.id)
    return_dict = {}

    profile = Profile.objects.get(user=idx)
    profile_sz = ProfileSerializer(profile)
    return_dict.update(profile_sz.data)

    if user.id == idx:
        return_dict.update({'is_user':1})
    
    return Response(return_dict, status=status.HTTP_200_OK)