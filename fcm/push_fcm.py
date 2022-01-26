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

def loop_request_fcm(token, req_from):
    message = messaging.Message(notification=messaging.Notification(
        title='루프요청',
        body='{0}님이 루프요청 하셨습니다'.format(req_from)
    ),
    data={
        'type':'request'
    },
    token = token,
    )
    messaging.send(message)

def loop_allow_fcm(token, req_from):
    message = messaging.Message(notification=messaging.Notification(
        title='루프요청',
        body='{0}님이 루프요청을 수락 하셨습니다'.format(req_from)
    ),
    data={
        'type':'allow'
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