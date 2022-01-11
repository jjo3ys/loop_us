from user_api.serializers import SimpleProfileSerializer
from user_api.models import Profile
from fcm.push_fcm import chat_fcm
from fcm.models import FcmToken

from .models import Msg, Room
from .serializer import ChatSerializer

from rest_framework import status
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated

@api_view(['POST', 'GET'])
@permission_classes((IsAuthenticated,))
def chatting(request, receiver_idx):
    user = request.user
    member_list=[user.id, int(receiver_idx)]    
    member_list.sort()
    if request.method == 'GET':     
        room = Room.objects.get(member=member_list)
        message_obj = Msg.objects.filter(room_id=room.id)

        for msg in message_obj:
            if msg.receiver_id == user.id and not msg.is_read:
                msg.is_read = True
                msg.save()

        message = ChatSerializer(message_obj, many=True).data

        return Response(message, status=status.HTTP_200_OK)

    if request.method == 'POST':
        room = Room.objects.get_or_create(member=member_list)[0]
        msg = Msg.objects.create(room_id=room.id,
                                 receiver_id=receiver_idx,
                                 message=request.data['message'],
                                 is_read=False)
                    
        message = ChatSerializer(msg).data

        try:
            send_profile = Profile.objects.get(user_id=user.id) 
            receiver_token = FcmToken.objects.get(user_id=receiver_idx)    
            chat_fcm(receiver_token.token, send_profile.real_name, request.data['message'])     
        except:
            pass

        return Response(message, status=status.HTTP_200_OK)

@api_view(['GET'])
@permission_classes((IsAuthenticated,))
def get_list(request):
    room = Room.objects.filter(member__icontains=request.user.id)
    return_list = []
    for r in room:
        last = ChatSerializer(list(Msg.objects.filter(room_id=r.id))[-1]).data
        not_read = Msg.objects.filter(room_id=r.id, is_read=False).count()
        r.member.remove(request.user.id)
        profile = SimpleProfileSerializer(Profile.objects.get(user_id=r.member[0])).data
        return_list.append({"profile":profile,
                            "message":last,
                            "not_read":not_read})

    return Response(return_list, status=status.HTTP_200_OK)