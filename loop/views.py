from .models import Loopship
from user_api.models import InterestCompany, Profile, Company_Inform
from user_api.serializers import SimpleComapnyProfileSerializer, SimpleProfileSerializer
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
        is_student = int(request.GET['is_student'])
        if is_student and Company_Inform.objects.filter(user_id=idx).exists():
                obj, created = InterestCompany.objects.get_or_create(company=idx, user_id=user.id)
                if not created:
                    obj.delete()
                    InterestCompany.objects.create(company=idx, user_id=user.id)
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
    user_follow = dict(Loopship.objects.filter(user_id=request.user.id).values_list('friend_id', 'user_id'))
    user_following = dict(Loopship.objects.filter(friend_id=request.user.id).values_list('user_id', 'friend_id'))
    if type == 'following':
        loop_list = Loopship.objects.filter(user=idx).values_list('friend_id', flat=True)
        corp_sz = SimpleComapnyProfileSerializer(Company_Inform.objects.filter(user_id__in=loop_list).select_related('company_logo'), many=True).data
        profile_sz = SimpleProfileSerializer(Profile.objects.filter(user_id__in=loop_list).select_related('department', 'school'), many=True).data
        for l in profile_sz:
            if l['user_id'] == request.user.id:
                l.update({"is_user":1})
            else:
                follow = l['user_id'] in user_follow
                following = l['user_id'] in user_following
                if follow and following:
                    l.update({"looped":3})
                elif follow:
                    l.update({"looped":2})
                elif following:
                    l.update({"looped":1})
                else:
                    l.update({"looped":0})
                l.update({"is_user":0})
                
        for l in corp_sz:
            if l['user_id'] == request.user.id:
                l.update({"is_user":1})
            else:
                follow = l['user_id'] in user_follow
                following = l['user_id'] in user_following
                if follow and following:
                    l.update({"looped":3})
                elif follow:
                    l.update({"looped":2})
                elif following:
                    l.update({"looped":1})
                else:
                    l.update({"looped":0})
                l.update({"is_user":0})
        return Response({"follow":profile_sz, 'corp_follow':corp_sz}, status=status.HTTP_200_OK)

    elif type == 'follower':
        loop_list = Loopship.objects.filter(friend_id = idx).values_list('user_id', flat=True)
        corp_sz = SimpleComapnyProfileSerializer(Company_Inform.objects.filter(user_id__in=loop_list).select_related('company_logo'), many=True).data
        profile_sz = SimpleProfileSerializer(Profile.objects.filter(user_id__in=loop_list).select_related('department', 'school'), many=True).data
        for l in profile_sz:
            if l['user_id'] == request.user.id:
                l.update({"is_user":1})
            else:
                follow = l['user_id'] in user_follow
                following = l['user_id'] in user_following
                if follow and following:
                    l.update({"looped":3})
                elif follow:
                    l.update({"looped":2})
                elif following:
                    l.update({"looped":1})
                else:
                    l.update({"looped":0})
                l.update({"is_user":0})
                
        for l in corp_sz:
            if l['user_id'] == request.user.id:
                l.update({"is_user":1})
            else:
                follow = l['user_id'] in user_follow
                following = l['user_id'] in user_following
                if follow and following:
                    l.update({"looped":3})
                elif follow:
                    l.update({"looped":2})
                elif following:
                    l.update({"looped":1})
                else:
                    l.update({"looped":0})
                l.update({"is_user":0})
        
        return Response({"follow":profile_sz, 'corp_follow':corp_sz}, status=status.HTTP_200_OK)