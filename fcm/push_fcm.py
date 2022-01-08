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