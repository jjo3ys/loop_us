from user_api.serializers import SimpleProfileSerializer
from user_api.models import Banlist, Profile
from fcm.push_fcm import chat_fcm
from fcm.models import FcmToken

from .models import Msg, Room
from .serializer import ChatSerializer

from rest_framework import status
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated

@api_view(['POST', 'GET', 'PUT'])
@permission_classes((IsAuthenticated,))
def chatting(request):
    user = request.user
    member_list=[user.id, int(request.GET['id'])]    
    member_list.sort()
    if request.method == 'GET':     
        return_dict = {}
        try:
            room = Room.objects.get(member=member_list)
        except Room.DoesNotExist:
            return Response("Can't find Room", status=status.HTTP_404_NOT_FOUND)

        if request.GET['last'] == '0':
            message = Msg.objects.filter(room_id=room.id)
            if message.filter(receiver_id=user.id, is_read=False).exists():
                message.filter(receiver_id=user.id).update(is_read=True)
            message = list(message)[-50:]
            try:
                return_dict['profile'] = SimpleProfileSerializer(Profile.objects.filter(user_id=request.GET['id'])[0]).data
                if Banlist.objects.filter(user_id=request.user.id, banlist__contains=int(request.GET['id'])).exists():
                    return_dict['profile']['is_banned'] = 1
                elif Banlist.objects.filter(user_id=request.GET['id'], banlist__contains=int(request.user.id)).exists():
                    return_dict['profile']['is_banned'] = 2
                else:
                    return_dict['profile']['is_banned'] = 0
                    
            except IndexError:
                return_dict['profile'] = None
        else:
            message = list(Msg.objects.filter(room_id=room.id, id__lt=request.GET['last']))[-50:]

        return_dict['message'] = ChatSerializer(message, many=True).data
        
        return Response(return_dict, status=status.HTTP_200_OK)

    elif request.method == 'POST':
        room = Room.objects.get_or_create(member=member_list)[0]
        Msg.objects.create(room_id=room.id,
                           receiver_id=request.GET['id'],
                           message=request.data['message'],
                           is_read=False)
        
        try:
            send_profile = Profile.objects.filter(user_id=user.id)[0]
            receiver_token = FcmToken.objects.get(user_id=request.GET['id'])    
            chat_fcm(receiver_token.token, send_profile.real_name, request.data['message'], user.id) 
        except:
            pass

        return Response(status=status.HTTP_200_OK)
    
    elif request.method == 'PUT':
        message = Msg.objects.filter(room_id=Room.objects.get(member=member_list).id, receiver_id=user.id, is_read=False)
        message.update(is_read=True)
        
        return Response(status=status.HTTP_200_OK)

@api_view(['GET'])
@permission_classes((IsAuthenticated,))
def get_list(request):
    room = Room.objects.filter(member__icontains=request.user.id)
    return_list = []
    for r in room:
        msg_obj = Msg.objects.filter(room_id=r.id)
        try:
            profile = SimpleProfileSerializer(Profile.objects.filter(user_id=r.member[0])[0]).data
        except:
            profile = None

        return_list.append({"profile":profile,
                                "message":ChatSerializer(msg_obj.last()).data,
                                "not_read":msg_obj.filter(room_id=r.id, receiver_id=request.user.id, is_read=False).count()})


    return_list.sort(key=lambda x: x['message']['date'], reverse=True)
    return Response(return_list, status=status.HTTP_200_OK)

@api_view(['GET'])
@permission_classes((IsAuthenticated,))
def get_profile(request):
    
    return_list = []

    for member in eval(request.GET['members']):
      
        data = SimpleProfileSerializer(Profile.objects.get(user_id = int(member))).data

        if Banlist.objects.filter(user_id=request.user.id, banlist__contains=member).exists():
            data['is_banned'] = 1

        elif Banlist.objects.filter(user_id=request.GET['id'], banlist__contains=member).exists():
            data['is_banned'] = 2
        else:
            data['is_banned'] = 0

        return_list.append(data)
    
    return Response(return_list, status=status.HTTP_200_OK)
