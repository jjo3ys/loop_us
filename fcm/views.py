from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework import status


# Create your views here.
# @api_view(['POST', ])
# @permission_classes((IsAuthenticated,))
# def token(request):
#     user = request.user
#     token_obj = FcmToken.objects.get(user=user)
#     if token_obj.token != request.data['token']:
#         token_obj.token = request.data['token']
#         token_obj.save()
#         return Response("token is changed", status=status.HTTP_200_OK)
    
#     else:
#         return Response("token isn't changed", status=status.HTTP_200_OK)