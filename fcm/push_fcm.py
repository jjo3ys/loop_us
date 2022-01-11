from firebase_admin import messaging

def loop_fcm(token, req_from):
    message = messaging.Message(notification=messaging.Notification(
        title='루프요청',
        body='{0}님이 루프요청 하셨습니다'.format(req_from)
    ),
    token = token,
    # topic='37'
    )
    messaging.send(message)

def tag_fcm(token, req_from):
    message = messaging.Message(notification=messaging.Notification(
        title='태그',
        body='{0}님이 활동에 회원님을 태그하였습니다.'.format(req_from)
    ),
    token = token,
    # topic='37'
    )
    messaging.send(message)

def like_fcm(token, req_from):
    message = messaging.Message(notification=messaging.Notification(
        title='알림',
        body='{0}님이 회원님의 포스팅을 좋아합니다.'.format(req_from)
    ),
    token = token,
    )
    messaging.send(message)

def chat_fcm(token, req_from, msg):
    message = messaging.Message(notification=messaging.Notification(
        title='{0}님이 메세지를 남겼습니다.'.format(req_from),
        body=msg
    ),
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