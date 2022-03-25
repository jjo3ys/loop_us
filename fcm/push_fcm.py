from firebase_admin import messaging
from user_api.models import Alarm
    
def loop_fcm(token, req_from, id):
    alarm, valid = Alarm.objects.get_or_create(user_id=token.user_id, type=2, target_id=id, alarm_from_id=id)
    if valid:
        message = messaging.Message(notification=messaging.Notification(
            title='루프어스',
            body='{0}님이 회원님을 팔로우하기 시작했어요.'.format(req_from)
        ),
        data={
            'type':'follow',
            'real_name':req_from,
            'id':str(id)
        },
        token = token.token,
        )
        messaging.send(message)

def tag_fcm(token, req_from, from_id, project, id):
    alarm, valid = Alarm.objects.get_or_create(user_id=token.user_id, type=3, target_id=id, alarm_from_id=from_id)
    if valid:
        message = messaging.Message(notification=messaging.Notification(
            title='루프어스',
            body='{0}님이 {1}활동에 회원님을 태그했어요.'.format(req_from, project)
        ),
        data={
            'type':'tag',
            'id':str(id)
        },
        token = token.token,
        )
        messaging.send(message)
    

def like_fcm(token, req_from, id, from_id):
    alarm, valid = Alarm.objects.get_or_create(user_id=token.user_id, type=4, target_id=id, alarm_from_id=from_id)
    if valid:
        message = messaging.Message(notification=messaging.Notification(
            title='루프어스',
            body='{0}님이 회원님의 포스팅을 좋아합니다.'.format(req_from)
        ),
        data={
            'type':'like',
            'id':str(id)
        },
        token = token.token,
        )
        messaging.send(message)

def comment_like_fcm(token, req_from, id, from_id):
    alarm, valid = Alarm.objects.get_or_create(user_id=token.user_id, type=5, target_id=id, alarm_from_id=from_id)
    if valid:
        message = messaging.Message(notification=messaging.Notification(
            title='루프어스',
            body='{0}님이 회원님의 댓글을 좋아합니다.'.format(req_from)
        ),
        data={
            'type':'comment_like',
            'id':str(id)
        },
        token = token.token,
        )
        messaging.send(message)


def chat_fcm(token, req_from, msg, user_id):
    message = messaging.Message(notification=messaging.Notification(
        title='{0}님'.format(req_from),
        body=msg
    ),
    data={
        "type":"msg",
        "real_name":req_from,
        "id":str(user_id)
    },
    token=token
    )
    messaging.send(message)

def notification_fcm(token_list):
    text = input("메세지:")
    msg = messaging.MulticastMessage(notification=messaging.Notification(
        title='공지',
        body=text
    ),
    tokens=token_list
    )
    messaging.send_multicast(msg)

def report_alarm(count, type, id, reason):
    if type == 0:
        text = '{0}번 유저가 신고 당함 누적 횟수:{1}'.format(id, count)
        report_type = 'user_report'
    elif type == 1:
        text = '{0}번 포스팅이 신고 당함 누적 횟수:{1}'.format(id, count)
        report_type = 'posting_report'
    elif type == 2:
        text = '{0}번 질문이 신고 당함 누적 횟수:{1}'.format(id, count)
        report_type = 'question_report'
    else:
        text = '{0}번 질문이 신고 당함 누적 횟수:{1}'.format(id, count)
        report_type = 'answer_report'

    message = messaging.Message(notification=messaging.Notification(
        title=text,
        body='사유:{0}'.format(reason)
    ),
    data={
        "type":report_type,
        "id":str(id)
    },
    token='e2x1oS_XT7iDENR1hVc6-T:APA91bE4K1Qa6vPfc7eeVlIfcdoW4c6YjgN-8jIlSWIlnEC3_OEXRtRRL6BNyUCnGI1iKoWcatb93scUPlsqgMTJ5hKMFnq2TVlyGUK57piHxmHnSZ5r7FFo9IuH591LxKEwjBizPK0j'
    )
    messaging.send(message)

def topic_alarm(topic, title):
    message = messaging.Message(notification=messaging.Notification(
        title=title,
        body='토픽으로 알람보내기'
    ),
    topic=topic
    )
    messaging.send(message)