from django.core.paginator import Paginator

from rest_framework import status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import api_view, permission_classes
from loop.models import Loopship

from scout_api.serializers import CompanyProfileSerializer, GroupSerializers
from tag.models import Group

from user_api.models import Company_Inform, Profile

@api_view(['GET'])
@permission_classes((IsAuthenticated,))
def recommendation_company(request):
    try:
        if request.GET['type'] == 0:
            return Response(CompanyProfileSerializer(Company_Inform.objects.filter(group = Profile.objects.filter(user = request.user)[0].group)[:5], many = True).data, status=status.HTTP_200_OK)
        elif request.GET['type'] == 1:
            return Response(CompanyProfileSerializer(Company_Inform.objects.filter(group = Company_Inform.objects.filter(user = request.user)[0].group)[:5], many = True).data, status=status.HTTP_200_OK)
            
    except:
        return Response(status=status.HTTP_204_NO_CONTENT)

    
@api_view(['GET'])
@permission_classes((IsAuthenticated,))
def company_group(request):
    try:
        if request.GET['type'] == 'main':
        
            group_obj = Group.objects.all()
            group_obj = Paginator(group_obj, 3)

            if group_obj.num_pages < int(request.GET['page']):

                return Response(status=status.HTTP_204_NO_CONTENT)
            
            small_group = GroupSerializers(group_obj.get_page(request.GET['page']), many=True).data

            for group in small_group:
                for company in group['companies']:

                    follow = Loopship.objects.filter(user_id=request.user.id, friend_id=company['user']).exists()
                    following = Loopship.objects.filter(user_id=company['user'], friend_id=request.user.id).exists()

                    if follow and following:
                        company.update({'looped':3})
                    elif follow:
                        company.update({'looped':2})
                    elif following:
                        company.update({'looped':1})
                    else:
                        company.update({'looped':0})

            return Response(small_group, status=status.HTTP_200_OK)

        else:
            company_obj = Company_Inform.objects.filter(group = request.GET['type']).order_by('-id')
            company_obj = Paginator(company_obj, 10)
            if company_obj.num_pages < int(request.GET['page']):
                return Response(status=status.HTTP_204_NO_CONTENT)

            companies = CompanyProfileSerializer(company_obj.get_page(request.GET['page']), many=True).data
            for company in companies:

                follow = Loopship.objects.filter(user_id=request.user.id, friend_id=company['user']).exists()
                following = Loopship.objects.filter(user_id=company['user'], friend_id=request.user.id).exists()

                if follow and following:
                    company.update({'looped':3})
                elif follow:
                    company.update({'looped':2})
                elif following:
                    company.update({'looped':1})
                else:
                    company.update({'looped':0})

        return Response(companies, status=status.HTTP_200_OK)
    except:
        return Response(status=status.HTTP_204_NO_CONTENT)


