from rest_framework.permissions import BasePermission

from user_api.models import Banlist

class Ban(BasePermission):
    def has_permission(self, request, view, obj):
        if request.user.is_authenticate:
            if request.user.id in Banlist.objects.filter(user_id=obj.id):
                return False

            elif obj.user.id in Banlist.objects.filter(user_id=request.user.id):
                return False
                
            else:
                return True

    def has_object_permission(self, request, view, obj):

        if request.user.id in Banlist.objects.filter(user_id=obj.id):
           return False

        elif obj.user.id in Banlist.objects.filter(user_id=request.user.id):
            return False

        else:
            return True
