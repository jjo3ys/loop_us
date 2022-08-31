from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework import status

from firebase_admin import messaging
from firebase_admin._messaging_utils import UnregisteredError
# Create your views here.
# @api_view(['POST', ])
# @permission_classes((IsAuthenticated,))
# def token(request):
#     user = request.user
#     token_obj = FcmToken.objects.get(user=user)
#     if token_obj.token != request.data['token']:
#         token_obj.token = request.data['token']
#         token_obj.save()
#         return Response("token is changed", status=status.HTTP_200_OK)
    
#     else:
#         return Response("token isn't changed", status=status.HTTP_200_OK)

@api_view(['POST', ])       #os 측 알람 2개 방지하기 위해서는 아래와 같은 설정이 필요
def test(requset):
    message = messaging.Message(
        android = messaging.AndroidConfig(notification=messaging.AndroidNotification(channel_id='high_importance_channel', icon='',  color='#f45342', sound='default')),
        notification= messaging.Notification(title='hi', body='ihi'),
    data={
       'room_id': '16', 
       'sender': '297', 
       'type': 'msg',
    },
    topic=str(143),
    )

    messaging.send(message)
    

    return Response("token isn't changed", status=status.HTTP_200_OK)