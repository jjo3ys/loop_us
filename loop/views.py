from .models import Loopship
from user_api.models import Profile
from user_api.serializers import SimpleProfileSerializer
from fcm.push_fcm import loop_fcm
# from fcm.models import FcmToken

from rest_framework import status
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated

# @api_view(['POST', 'DELETE'])
# @permission_classes((IsAuthenticated,))
# def loop_request(request, idx):
#     user = request.user
#     if request.method == 'POST': 
#         try:
#             request = Request.objects.get(From_id=idx, To_id=user.id)
#             profile = Profile.objects.get(user_id=user.id)
#             token = FcmToken.objects.get(user_id=idx)
#             loop_allow_fcm(token.token, profile.real_name)

#             Loopship.objects.create(user_id=user.id, friend_id=idx)
#             Loopship.objects.create(user_id=idx, friend_id=user.id)
#             request.delete()

#             return Response("ok", status=status.HTTP_200_OK)  

#         except:
#             Request.objects.create(From_id=user.id, To_id=idx, is_active=False)
#             profile = Profile.objects.get(user_id=user.id)
#             token_obj = FcmToken.objects.get(user_id=idx)
#             loop_request_fcm(token_obj.token, profile.real_name)
#             return Response("ok", status=status.HTTP_200_OK)
    
#     elif request.method == 'DELETE':
#         try:
#             request = Request.objects.get(From_id=user.id, To_id=idx)
#             request.delete()
        
#             return Response("delete", status=status.HTTP_200_OK)
#         except:
#             request

@api_view(['POST'])
@permission_classes((IsAuthenticated,))
def loop(request, idx):
    user = request.user
    try:
        profile = Profile.objects.filter(user_id=user.id)[0]
        loop_fcm(idx, profile.real_name, user.id)

        Loopship.objects.get_or_create(user_id=user.id, friend_id=idx)
    
        return Response("ok", status=status.HTTP_200_OK)
    except:
        return Response(status=status.HTTP_404_NOT_FOUND)

@api_view(['DELETE'])
@permission_classes((IsAuthenticated,))
def unloop(request, idx):
    user = request.user

    loopship_obj = Loopship.objects.get(user=user, friend=idx)
    loopship_obj.delete()

    return Response("ok", status=status.HTTP_200_OK)
    
@api_view(['GET'])
@permission_classes((IsAuthenticated,))
def get_list(request, type, idx):
    if type == 'following':
        loop_list = Loopship.objects.filter(user=idx).values_list('friend_id', flat=True)
        profile_sz = SimpleProfileSerializer(Profile.objects.filter(user_id__in=loop_list).select_related('department', 'school'), many=True).data
        for l in profile_sz:
            if l['user_id'] == request.user.id:
                l.update({"is_user":1})
            else:
                # follow = Loopship.objects.filter(user_id=request.user.id, friend_id=l.friend_id).exists()
                # following = Loopship.objects.filter(user_id=l.friend_id, friend_id=request.user.id).exists()
                # if follow and following:
                #     profile_sz.update({"looped":3})
                # elif follow:
                #     profile_sz.update({"looped":2})
                # elif following:
                #     profile_sz.update({"looped":1})
                # else:
                #     profile_sz.update({"looped":0})
                l.update({"is_user":0})
        return Response({"follow":profile_sz}, status=status.HTTP_200_OK)

    elif type == 'follower':
        loop_list = Loopship.objects.filter(friend_id = idx).values_list('user_id', flat=True)
        profile_sz = SimpleProfileSerializer(Profile.objects.filter(user_id__in=loop_list).select_related('department', 'school'), many=True).data
        for l in profile_sz:
            if l['user_id'] == request.user.id:
                l.update({"is_user":1})
            else:
                l.update({"is_user":0})
        
        return Response({"follow":profile_sz}, status=status.HTTP_200_OK)