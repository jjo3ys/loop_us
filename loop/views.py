from .serializers import LoopSerializer, ProfileSerializer
from .models import Loopship
from user_api.models import Profile

from django.contrib.auth.models import User
from django.db.models import Q

from rest_framework import status
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated

@api_view(['POST'])
@permission_classes((IsAuthenticated,))
def loop(request, idx):
    user = request.user
    friend = User.objects.get(id=idx)

    Loopship.objects.create(user=user, friend=friend)
    Loopship.objects.create(user=friend, friend=user)
 
    return Response("ok", status=status.HTTP_200_OK)

@api_view(['POST'])
@permission_classes((IsAuthenticated,))
def unloop(request, idx):
    user = request.user
    unfriend = User.objects.get(id=idx)

    loopship_obj = Loopship.objects.get(user=user, friend=unfriend)
    loopship_obj.delete()
    loopship_obj = Loopship.objects.get(user=unfriend, friend=user)
    loopship_obj.delete()

@api_view(['GET'])
@permission_classes((IsAuthenticated,))
def get_list(request, idx):
    return_dict = {}
    friend_list = []
    loop_obj = Loopship.objects.filter(user=idx)
    loop_sz = LoopSerializer(loop_obj, many = True)

    for l in loop_sz.data:
        try:
            profile_obj = Profile.objects.get(user_id=l['friend'])
            profile_sz = ProfileSerializer(profile_obj)
            friend_list.append(profile_sz.data)
            
        except Profile.DoesNotExist:
            continue

    return_dict.update({"friend":friend_list})           
    return Response(return_dict, status=status.HTTP_200_OK)