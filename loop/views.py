from .models import Loopship
from user_api.models import Profile
from user_api.serializers import SimpleProfileSerializer
from fcm.push_fcm import loop_allow_fcm
from fcm.models import FcmToken

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
    profile = Profile.objects.get(user_id=user.id)
    token = FcmToken.objects.get(user_id=idx)
    loop_allow_fcm(token.token, profile.real_name)

    Loopship.objects.create(user_id=user.id, friend_id=idx)
 
    return Response("ok", status=status.HTTP_200_OK)

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
        following_list = []
        loop_obj = Loopship.objects.filter(user=idx)

        for l in loop_obj:
            profile_sz = SimpleProfileSerializer(Profile.objects.get(user_id=l.friend_id)).data
            if l.friend_id == request.user.id:
                profile_sz.update({"is_user":1})
            else:
                profile_sz.update({"is_user":0})
            following_list.append(profile_sz)

        return Response({"follow":following_list}, status=status.HTTP_200_OK)

    elif type == 'follower':
        follwer_list = []
        loop_obj = Loopship.objects.filter(friend_id = idx)
        
        for l in loop_obj:
            profile_sz = SimpleProfileSerializer(Profile.objects.get(user_id=l.user_id)).data
            if l.user_id == request.user.id:
                profile_sz.update({"is_user":1})
            else:
                profile_sz.update({"is_user":0})
            follwer_list.append(profile_sz)

    return Response({"follow":follwer_list}, status=status.HTTP_200_OK)