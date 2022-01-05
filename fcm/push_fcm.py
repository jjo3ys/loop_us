from firebase_admin import messaging

def send_fcm(token, req_from):
    message = messaging.Message(notification=messaging.Notification(
        title='루프요청',
        body='{0}님이 루프요청 하셨습니다'.format(req_from)
    ),
    token = token,
    # topic='37'
    )
    messaging.send(message)