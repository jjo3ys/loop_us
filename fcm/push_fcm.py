from firebase_admin import messaging

def answer_fcm(token, req_from, id):
    message = messaging.Message(notification=messaging.Notification(
        title='답글',
        body='회원님의 질문에 {0}님이 답변을 남겼습니다.'.format(req_from)
    ),
    data={
        'type':'answer',
        'id':str(id)
    },
    token = token,
    )
    messaging.send(message)

def adopt_fcm(token):
    message = messaging.Message(notification=messaging.Notification(
        title='채택',
        body='회원님의 답글이 채택되었습니다.'
    ),
    data={
        'type':'adopt'
    },
    token = token,
    )
    messaging.send(message)

def loop_fcm(token, req_from):
    message = messaging.Message(notification=messaging.Notification(
        title='팔로우',
        body='{0}님이 회원님을 팔로우 합니다.'.format(req_from)
    ),
    data={
        'type':'follow'
    },
    token = token,
    )
    messaging.send(message)
def tag_fcm(token, req_from):
    message = messaging.Message(notification=messaging.Notification(
        title='태그',
        body='{0}님이 활동에 회원님을 태그하였습니다.'.format(req_from)
    ),
    data={
        'type':'tag'
    },
    token = token,
    )
    messaging.send(message)

def like_fcm(token, req_from):
    message = messaging.Message(notification=messaging.Notification(
        title='알림',
        body='{0}님이 회원님의 포스팅을 좋아합니다.'.format(req_from)
    ),
    data={
        'type':'tag',
        'id':str(id)
    },
    token = token,
    )
    messaging.send(message)

def chat_fcm(token, req_from, msg, user_id):
    message = messaging.Message(notification=messaging.Notification(
        title='{0}님이 메세지를 남겼습니다.'.format(req_from),
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