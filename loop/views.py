from .serializers import LoopSerializer
from .models import Loopship, Request
from user_api.models import Profile
from user_api.serializers import SimpleProfileSerializer as ProfileSerializer
from fcm.push_fcm import loop_fcm
from fcm.models import FcmToken

from django.contrib.auth.models import User
from django.db.models import Q

from rest_framework import status
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated

@api_view(['POST'])
@permission_classes((IsAuthenticated,))
def loop_request(request, idx):
    user = request.user
    try:
        Request.objects.create(From_id=user.id, To_id=idx, is_active=False)
        profile = Profile.objects.get(user_id=user.id)
        token_obj = FcmToken.objects.get(user_id=idx)
        loop_fcm(token_obj.token, profile.real_name)
        return Response("ok", status=status.HTTP_200_OK)
    
    except:
        return Response("Nan", status=status.HTTP_404_NOT_FOUND)

@api_view(['GET'])
@permission_classes((IsAuthenticated,))
def loop(request, idx):
    user = request.user
    Request.objects.get(From_id=idx, To_id=user.id).delete()

    Loopship.objects.create(user_id=user.id, friend_id=idx)
    Loopship.objects.create(user_id=idx, friend_id=user.id)
 
    return Response("ok", status=status.HTTP_200_OK)

@api_view(['GET'])
@permission_classes((IsAuthenticated,))
def unloop(request, idx):
    user = request.user
    unfriend = User.objects.get(id=idx)

    loopship_obj = Loopship.objects.get(user=user, friend=unfriend)
    loopship_obj.delete()
    loopship_obj = Loopship.objects.get(user=unfriend, friend=user)
    loopship_obj.delete()

    return Response("ok", status=status.HTTP_200_OK)
    
@api_view(['GET'])
@permission_classes((IsAuthenticated,))
def get_list(request, idx):
    return_dict = {}
    friend_list = []
    myfriend_list = []

    my_loop_obj = Loopship.objects.filter(user=request.user.id)
    my_sz = LoopSerializer(my_loop_obj, many = True).data
    for d in my_sz:
        myfriend_list.append(d['friend'])

    loop_obj = Loopship.objects.filter(user=idx)
    loop_sz = LoopSerializer(loop_obj, many = True).data

    for l in loop_sz:
        try:
            profile_obj = Profile.objects.get(user_id=l['friend'])
            profile_sz = ProfileSerializer(profile_obj).data
            if l['friend'] == request.user.id:
                profile_sz.update({"is_user":1})
            elif l['friend'] in myfriend_list:
                profile_sz.update({"is_user":0})
                profile_sz.update({"looped":1})
            else:
                profile_sz.update({"is_user":0})
                profile_sz.update({"looped":0})
                try:
                    Request.objects.get(From_id=request.user.id, To_id=idx)
                    profile_sz.update({"requested":1})
                except:
                    profile_sz.update({"requested":0})
                    
            friend_list.append(profile_sz)
            
        except Profile.DoesNotExist:
            continue

    return_dict.update({"friend":friend_list})           
    return Response(return_dict, status=status.HTTP_200_OK)