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
    first = request.user
    Loopship.objects.create(first=first, second_id=idx)

    return Response("ok", status=status.HTTP_200_OK)

@api_view(['GET'])
@permission_classes((IsAuthenticated,))
def get_list(request, idx):
    return_dict = {}
    loop_obj = Loopship.objects.filter(Q(first=idx) | Q(second=idx) & Q(active=True))
    loop_sz = LoopSerializer(loop_obj, many = True)
    for l in loop_sz.data:
        if l['first'] == idx:
            friend = l['second']
        else:
            friend = l['first']
        profile_obj = Profile.objects.get(user_id=friend)
        profile_sz = ProfileSerializer(profile_obj)
        return_dict.update({"friend":profile_sz.data})
    return Response(return_dict, status=status.HTTP_200_OK)