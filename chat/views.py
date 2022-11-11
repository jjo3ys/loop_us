from user_api.serializers import SimpleComapnyProfileSerializer, SimpleProfileSerializer
from user_api.models import Banlist, Company_Inform, Profile
from fcm.push_fcm import chat_fcm
# from fcm.models import FcmToken

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
            chat_fcm(request.GET['id'], send_profile.real_name, request.data['message'], user.id) 
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

    member = eval(request.GET['members'])

    profiles = (SimpleProfileSerializer(Profile.objects.filter(user_id__in=member).select_related('school', 'department'), many=True).data
                    + SimpleComapnyProfileSerializer(Company_Inform.objects.filter(user_id__in=member).select_related('company_logo'), many=True).data)

    user_banned = list(Banlist.objects.filter(banlist__contains=request.user.id).values_list('user_id', flat=True))
    user_ban = Banlist.objects.filter(user_id=request.user.id)[0].banlist
    for profile in profiles:
        if profile['user_id'] in user_banned:      # 상대 유저가 나를 차단해서 나의 채팅방에 알수없음으로 표시
            profile['is_banned'] = 2
        elif profile['user_id'] in user_ban:
            profile['is_banned'] = 1
        else:       
            profile['is_banned'] = 0
        member.remove(profile['user_id'])

    return Response({'profile':profiles, 'none':member}, status=status.HTTP_200_OK)