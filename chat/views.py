from user_api.serializers import SimpleProfileSerializer
from user_api.models import Profile

from .models import Msg
from .serializer import ChatSerializer

from rest_framework import status
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from django.db.models import Q

@api_view(['POST', 'GET'])
@permission_classes((IsAuthenticated,))
def chatting(request, receiver_idx):
    user = request.user
    if request.method == 'GET':
        
        send_msg = Msg.objects.filter(sender_id=user.id, receiver_id=receiver_idx)
        receive_msg = Msg.objects.filter(sender_id=receiver_idx, receiver_id=user.id)
        message_obj = receive_msg.union(send_msg).order_by('id')
        
        for msg in receive_msg:
            msg.is_read = True
            msg.save()

        message = ChatSerializer(message_obj, many=True).data
        return_dict = {"messages":message}
        profile = Profile.objects.get(user_id=receiver_idx)
        profile = SimpleProfileSerializer(profile).data
        return_dict.update(profile)

        return Response(return_dict, status=status.HTTP_200_OK)

    if request.method == 'POST':
        msg = Msg.objects.create(sender_id=user.id,
                                 receiver_id=receiver_idx,
                                 message=request.data['message'],
                                 is_read=False)
                                 
        message = ChatSerializer(msg).data
        profile = Profile.objects.get(user_id=receiver_idx)
        profile = SimpleProfileSerializer(profile).data
        message.update(profile)

        return Response(message, status=status.HTTP_200_OK)