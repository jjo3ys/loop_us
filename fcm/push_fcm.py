from firebase_admin import messaging
from user_api.models import Alarm

def answer_fcm(token, req_from, question, id):
    message = messaging.Message(notification=messaging.Notification(
        title=question,
        body='질문에 어떤 답변이 달렸는지 확인해보세요.'.format(req_from)
    ),
    data={
        'type':'answer',
        'id':str(id)
    },
    token = token.token,
    )
    messaging.send(message)
    Alarm.objects.create(user_id=token.user_id, type=1, target_id=id)

def loop_fcm(token, req_from, id):
    message = messaging.Message(notification=messaging.Notification(
        title='루프어스',
        body='{0}님이 회원님을 팔로우하기 시작했어요.'.format(req_from)
    ),
    data={
        'type':'follow',
        'id':str(id)
    },
    token = token.token,
    )
    messaging.send(message)
    Alarm.objects.create(user_id=token.user_id, type=2, target_id=id)

def tag_fcm(token, req_from, project, id):
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
    Alarm.objects.create(user_id=token.user_id, type=3, target_id=id)

def like_fcm(token, req_from, id):
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
    Alarm.objects.create(user_id=token.user_id, type=4, target_id=id)

def chat_fcm(token, req_from, msg, user_id):
    message = messaging.Message(notification=messaging.Notification(
        title='{0}님'.format(req_from),
        body=msg
    ),
    data={
        "type":"msg",
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
    if type == True:
        text = '{0}번 유저가 신고 당함 누적 횟수:{1}'.format(id, count)
        report_type = 'user_report'
    elif type == False:
        text = '{0}번 포스팅이 신고 당함 누적 횟수:{1}'.format(id, count)
        report_type = 'posting_report'

    message = messaging.Message(notification=messaging.Notification(
        title=text,
        body='사유:{0}'.format(reason)
    ),
    data={
        "type":report_type,
        "id":str(id)
    },
    token='f2PsSd8nTMadfikWkOdCaQ:APA91bFZxp85MUCx00WSuavTAVeNyOPudSfdE74W5xDZaQe-0WyxP3SF9VNtCzd_sgGib_qYEJX4QkkntXoaliSHAqQmyD9tAtSw4pWbC6ScU28BkZCa4YLFb_u84lRY_-dR2uP9Z4D6'
    )
    messaging.send(message)