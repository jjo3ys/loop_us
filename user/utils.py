from django.core.mail import EmailMessage, EmailMultiAlternatives
from elasticsearch import Elasticsearch

import datetime
import random
import redis

ES = Elasticsearch('localhost:9200')
CLIENT = redis.Redis()

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