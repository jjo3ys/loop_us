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
        if int(request.GET['type']) == 0:
            stud_group = Profile.objects.filter(user = request.user)[0].group
            if stud_group == 16:
                return Response(CompanyProfileSerializer(Company_Inform.objects.all().order_by('-view_count')[:5], many = True).data, status=status.HTTP_200_OK)

            return Response(CompanyProfileSerializer(Company_Inform.objects.filter(group = stud_group).order_by('-view_count')[:5], many = True).data, status=status.HTTP_200_OK)
        elif int(request.GET['type']) == 1:
            return Response(CompanyProfileSerializer(Company_Inform.objects.filter(group = Company_Inform.objects.filter(user = request.user)[0].group).order_by('-view_count')[:5], many = True).data, status=status.HTTP_200_OK)
            
    except:
        return Response(status=status.HTTP_204_NO_CONTENT)

@api_view(['GET'])
@permission_classes((IsAuthenticated,))
def company_group(request):

        if request.GET['type'] == 'main':
        
            group_obj = Group.objects.all()
            group_obj = Paginator(group_obj, 3)

            if group_obj.num_pages < int(request.GET['page']):
                return Response(status=status.HTTP_204_NO_CONTENT)
                
            return Response(GroupSerializers(group_obj.get_page(request.GET['page']), many=True).data, status=status.HTTP_200_OK)

        else:
            company_obj = Company_Inform.objects.filter(group = request.GET['type']).order_by('?')
            company_obj = Paginator(company_obj, 10)

            if company_obj.num_pages < int(request.GET['page']):
                return Response(status=status.HTTP_204_NO_CONTENT)

        return Response(CompanyProfileSerializer(company_obj.get_page(request.GET['page']), many=True).data, status=status.HTTP_200_OK)


