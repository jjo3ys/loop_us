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
# from .serializers import ProfileSerializer, UserSerializer

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

    for i in range(6):
        time.sleep(30)
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
            Profile.objects.create(user = user_obj,
                                    type = request.data['type'],
                                    real_name = request.data['real_name'],
                                    class_num = request.data['class_num'],
                                    profile_image = request.data['image'])
        except:
            token.delete()
            return Response('Profile information is not invalid', status=status.HTTP_404_NOT_FOUND)

        return Response({'message':'singup success',
                         'token':str(token),
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

# @api_view(['GET', ])
# def profile_load(reuqest, idx):
#     try:
#         profile = Profile.objects.get(user=idx)

#     except:
#         return Response('해당 유저의 프로필이 유효하지 않습니다.', status=status.HTTP_404_NOT_FOUND)