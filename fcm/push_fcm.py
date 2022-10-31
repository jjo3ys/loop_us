from firebase_admin import messaging
from firebase_admin._messaging_utils import UnregisteredError, QuotaExceededError
# from fcm.models import FcmToken
from user_api.models import Alarm
    
def loop_fcm(topic, req_from, id):
    alarm, valid = Alarm.objects.get_or_create(user_id=topic, type=2, target_id=id, alarm_from_id=id)
    if valid:
        message = messaging.Message(
            android = messaging.AndroidConfig(notification=messaging.AndroidNotification(channel_id='high_importance_channel', sound='default')),
            apns= messaging.APNSConfig(payload=messaging.APNSPayload(aps=messaging.Aps(sound='default'))),
            notification=messaging.Notification(
                title='루프어스',
                body='{0}님이 회원님을 팔로우하기 시작했어요.'.format(req_from)
            ),
            data={
                'type':'2',
                'real_name':req_from,
                'id':str(id),
                'sender_id':str(id)
            },
            topic=str(topic)
            )
        try:
            messaging.send(message)
        except QuotaExceededError:
            pass

def tag_fcm(topic, req_from, from_id, project, id):
    alarm, valid = Alarm.objects.get_or_create(user_id=topic, type=3, target_id=id, alarm_from_id=from_id)
    if valid:
        message = messaging.Message(
            android = messaging.AndroidConfig(notification=messaging.AndroidNotification(channel_id='high_importance_channel', sound='default')),
            apns= messaging.APNSConfig(payload=messaging.APNSPayload(aps=messaging.Aps(sound='default'))),
            notification=messaging.Notification(
                title='루프어스',
                body='{0}님이 {1}활동에 회원님을 태그했어요.'.format(req_from, project)
            ),
            data={
                'type':'3',
                'id':str(id),
                'sender_id':str(from_id)
            },
            topic=str(topic),
            )
        try:
            messaging.send(message)
        except QuotaExceededError:
            pass

def like_fcm(topic, req_from, id, from_id):
    alarm, valid = Alarm.objects.get_or_create(user_id=topic, type=4, target_id=id, alarm_from_id=from_id)
    if valid:
        message = messaging.Message(
            android = messaging.AndroidConfig(notification=messaging.AndroidNotification(channel_id='high_importance_channel', sound='default')),
            apns= messaging.APNSConfig(payload=messaging.APNSPayload(aps=messaging.Aps(sound='default'))),
            notification=messaging.Notification(
                title='루프어스',
                body='{0}님이 회원님의 포스팅을 좋아합니다.'.format(req_from)
            ),
            data={
                'type':'4',
                'id':str(id),
                'sender_id':str(from_id)
            },
            topic=str(topic),
            )
        try:
            messaging.send(message)
        except QuotaExceededError:
            pass

def comment_like_fcm(topic, req_from, id, from_id, post_id):
    alarm, valid = Alarm.objects.get_or_create(user_id=topic, type=5, target_id=id, alarm_from_id=from_id)
    if valid:
        message = messaging.Message(
            android = messaging.AndroidConfig(notification=messaging.AndroidNotification(channel_id='high_importance_channel', sound='default')),
            apns= messaging.APNSConfig(payload=messaging.APNSPayload(aps=messaging.Aps(sound='default'))),
                notification=messaging.Notification(
                title='루프어스',
                body='{0}님이 회원님의 댓글을 좋아합니다.'.format(req_from)
            ),
            data={
                'type':'5',
                'id':str(id),
                'post_id':str(post_id),
                'sender_id':str(from_id)
            },
            topic=str(topic),
            )
        try:
            messaging.send(message)
        except QuotaExceededError:
            pass

def cocomment_like_fcm(topic, req_from, id, from_id, post_id):
    alarm, valid = Alarm.objects.get_or_create(user_id=topic, type=6, target_id=id, alarm_from_id=from_id)
    if valid:
        message = messaging.Message(
            android = messaging.AndroidConfig(notification=messaging.AndroidNotification(channel_id='high_importance_channel', sound='default')),
            apns= messaging.APNSConfig(payload=messaging.APNSPayload(aps=messaging.Aps(sound='default'))),
            notification=messaging.Notification(
                title='루프어스',
                body='{0}님이 회원님의 대댓글을 좋아합니다.'.format(req_from)
            ),
            data={
                'type':'6',
                'id':str(id),
                'post_id':str(post_id),
                'sender_id':str(from_id)
            },
            topic=str(topic),
            )
        try:
            messaging.send(message)
        except QuotaExceededError:
            pass

def comment_fcm(topic, req_from, id, from_id):
    alarm, valid = Alarm.objects.get_or_create(user_id=topic, type=7, target_id=id, alarm_from_id=from_id)
    if valid:
        message = messaging.Message(
            android = messaging.AndroidConfig(notification=messaging.AndroidNotification(channel_id='high_importance_channel', sound='default')),
            apns= messaging.APNSConfig(payload=messaging.APNSPayload(aps=messaging.Aps(sound='default'))),
            notification=messaging.Notification(
                title='루프어스',
                body='{0}님이 회원님의 포스팅에 댓글을 남겼습니다.'.format(req_from)
            ),
            data={
                'type':'7',
                'id':str(id),
                'sender_id':str(from_id)
            },
            topic=str(topic),
            )
        try:
            messaging.send(message)
        except QuotaExceededError:
            pass

def cocomment_fcm(topic, req_from, id, from_id, post_id):
    alarm, valid = Alarm.objects.get_or_create(user_id=topic, type=8, target_id=id, alarm_from_id=from_id)
    if valid:
        message = messaging.Message(
            android = messaging.AndroidConfig(notification=messaging.AndroidNotification(channel_id='high_importance_channel', sound='default')),
            apns= messaging.APNSConfig(payload=messaging.APNSPayload(aps=messaging.Aps(sound='default'))),
            notification=messaging.Notification(
                title='루프어스',
                body='{0}님이 회원님의 댓글에 답글을 남겼습니다.'.format(req_from)
            ),
            data={
                'type':'8',
                'id':str(id),
                'post_id':str(post_id),
                'sender_id':str(from_id)
            },
            topic=str(topic),
            )
        try:
            messaging.send(message)
        except QuotaExceededError:
            pass
    
def chat_fcm(topic, req_from, msg, user_id):
    message = messaging.Message(
        android = messaging.AndroidConfig(notification=messaging.AndroidNotification(channel_id='high_importance_channel', sound='default')),
        apns= messaging.APNSConfig(payload=messaging.APNSPayload(aps=messaging.Aps(sound='default'))),
            notification=messaging.Notification(
            title='{0}님'.format(req_from),
            body=msg
        ),
        data={
            "type":"msg",
            "real_name":req_from,
            "id":str(user_id)
        },
        topic=str(topic)
        )
    try:
        messaging.send(message)
    except QuotaExceededError:
        pass
    
def department_fcm(topic, id, from_id):
    alarm, valid = Alarm.objects.get_or_create(user_id=topic, type=9, target_id=id, alarm_from_id=from_id)
    if valid:
        message = messaging.Message(
            android = messaging.AndroidConfig(notification=messaging.AndroidNotification(channel_id='high_importance_channel', sound='default')),
            apns= messaging.APNSConfig(payload=messaging.APNSPayload(aps=messaging.Aps(sound='default'))),
            notification=messaging.Notification(
                title='루프어스',
                body='새로운 학과공지가 올라왔습니다.'
            ),
            data={
                'type':'9',
                'id':str(id),
                'sender_id':str(from_id)
            },
            topic='department'+str(topic),
            )
        try:
            messaging.send(message)
        except QuotaExceededError:
            pass

def school_fcm(topic, id, from_id):
    alarm, valid = Alarm.objects.get_or_create(user_id=topic, type=9, target_id=id, alarm_from_id=from_id)
    if valid:
        message = messaging.Message(
            android = messaging.AndroidConfig(notification=messaging.AndroidNotification(channel_id='high_importance_channel', sound='default')),
            apns= messaging.APNSConfig(payload=messaging.APNSPayload(aps=messaging.Aps(sound='default'))),
            notification=messaging.Notification(
                title='루프어스',
                body='새로운 학교공지가 올라왔습니다.'
            ),
            data={
                'type':'9',
                'id':str(id),
                'sender_id':str(from_id)
            },
            topic='school'+str(topic),
            )
        try:
            messaging.send(message)
        except QuotaExceededError:
            pass

def rank_fcm(topic):
    message = messaging.Message(
        android = messaging.AndroidConfig(notification=messaging.AndroidNotification(channel_id='high_importance_channel', sound='default')),
        apns= messaging.APNSConfig(payload=messaging.APNSPayload(aps=messaging.Aps(sound='default'))),
        notification=messaging.Notification(
            title='루프어스',
            body='교내 사용자 랭킹이 업데이트 되었습니다.'
        ),
        data={
            'type':'10',
        },
        topic='school'+str(topic),
        )
    try:
        messaging.send(message)
    except QuotaExceededError:
        pass
        
def certify_fcm(topic):
    message = messaging.Message(
        android = messaging.AndroidConfig(notification=messaging.AndroidNotification(channel_id='high_importance_channel', sound='default')),
        apns= messaging.APNSConfig(payload=messaging.APNSPayload(aps=messaging.Aps(sound='default'))),
        data={
            "type":"certification",
        },
        topic=topic
        )
    try:
        messaging.send(message)
    except QuotaExceededError:
        pass

def notification_fcm(token_list):
    text = input("메세지:")
    msg = messaging.MulticastMessage(
        apns= messaging.APNSConfig(payload=messaging.APNSPayload(aps=messaging.Aps(sound='default'))),
        notification=messaging.Notification(
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

    message = messaging.Message(
        android = messaging.AndroidConfig(notification=messaging.AndroidNotification(channel_id='high_importance_channel', sound='default')),
        apns= messaging.APNSConfig(payload=messaging.APNSPayload(aps=messaging.Aps(sound='default'))),
        notification=messaging.Notification(
            title=text,
            body='사유:{0}'.format(reason)
        ),
        data={
            "type":report_type,
            "id":str(id)
        },
        topic='24'
        )
    try:
        messaging.send(message)
    except QuotaExceededError:
        pass

# def topic_alarm(topic, title):
#     message = messaging.Message(notification=messaging.Notification(
#         title=title,
#         body='토픽으로 알람보내기'
#     ),
#     topic=topic
#     )
#     try:
#         messaging.send(message)
#     except UnregisteredError:
#         pass

# def logout_push(token):
#     message = messaging.Message(
#         data={
#             "type":"logout"
#         },   
#         token=token
#     )
#     try:
#         messaging.send(message)
#     except UnregisteredError:
#         pass