from django.core.mail import EmailMessage, EmailMultiAlternatives
from elasticsearch import Elasticsearch

from .models import Loopship

import datetime
import random
import redis

ES = Elasticsearch('localhost:9200')
CLIENT = redis.Redis()

# 인증 메일
def send_msg(email):
    r = CLIENT.get(email.replace('@', ''))
    if not r:
        pass
    else:
        CLIENT.delete(email)
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
    CLIENT.set(email.replace('@', ''), certify_num, datetime.timedelta(seconds=180))

# 루프 상태
def loop(user, friend):
    follow = Loopship.objects.filter(user_id = user, friend_id = friend).exists()
    following = Loopship.objects.filter(user_id = friend, friend_id = user).exists()

    looped = 0                          # normal 상태
    if follow and following: looped = 3 # 맞팔
    elif follow:             looped = 2 # 상대방을 팔로우
    elif following:          looped = 1 # 상대방이 팔로우

    return looped

# 팔로우 팔로잉 카운트
def loop_count(target_id):
    follower_count  = Loopship.objects.filter(friend_id=target_id).count()
    following_count = Loopship.objects.filter(user_id=target_id).count()
    return {"follower":follower_count, "following":following_count}

def email_format(ask_type, data):
    # 일반 문의
    if ask_type == 'normal':
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

    # 학교 등록 문의    
    elif ask_type == 'school':
        message = EmailMessage(
            subject = '학교 등록 문의',
            body    = f'문의내용:{data["content"]}',
            to      = ['loopus@loopus.co.kr']
        )

    # 학과 등록 문의
    elif ask_type == 'department':
        message = EmailMessage(
            subject = f'{data["school"]} 학과 등록 문의',
            body    = f'문의 내용: {data["content"]}',
            to      = ['loopus@loopus.co.kr']
        )
    
    # 기업 회원가입 문의
    elif ask_type == 'company_signup':
        message = EmailMessage(
            subject = f'{data["company_name"]} 기업 회원가입 문의',
            body    = '첨부된 파일의 양식에 따라 작성하여 다시 보내주시면 검토하여 등록 후 이 메일을 통해 알려드리겠습니다.',
            to      = [data["email"]]
        )
        message.attach_file('./static/csv_format/signup_form.csv')

    # 기업 소개 수정 문의
    elif ask_type == 'company_info':
        message = EmailMessage(
            subject = f'{data["company_name"]} 기업 소개 수정 문의',
            body    = '첨부된 파일의 양식에 따라 작성하여 다시 보내주시면 검토하여 등록 후 이 메일을 통해 알려드리겠습니다.',
            to      = [data["email"]]
        )
        message.attach_file('./static/csv_format/edit_information_form.csv')
    
    return message