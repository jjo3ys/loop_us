from django.core.paginator import Paginator

from rest_framework import status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import api_view, permission_classes
from loop.models import Loopship

from scout_api.serializers import CompanyProfileSerializer

from user_api.models import Company_Inform, Profile

@api_view(['GET'])
@permission_classes((IsAuthenticated,))
def recommendation_company(request):
    return Response(CompanyProfileSerializer(Company_Inform.objects.filter(group =Profile.objects.get(user = request.user).group)[:5], many = True).data, status=status.HTTP_200_OK)


@api_view(['GET'])
@permission_classes((IsAuthenticated,))
def company_group(request):
    try:
        if request.GET['type'] == 'all':
            company_obj = Company_Inform.objects.filter(company_name__icontains=request.GET['query']).order_by('-category')
        
        else:
            company_obj = Company_Inform.objects.filter(company_name__icontains=request.GET['query'], group = request.GET['type']).order_by('-id')

        company_obj = Paginator(company_obj, 10)

        if company_obj.num_pages < int(request.GET['page']):
            return Response(status=status.HTTP_204_NO_CONTENT)

        companies = CompanyProfileSerializer(company_obj.get_page(request.GET['page']), many=True).data
        for company in companies:

            if Loopship.objects.filter(friend_id = company['user'], user= request.user).exists():
                company['is_follow'] = True
            else:
                company['is_follow'] = False

        return Response(companies, status=status.HTTP_200_OK)
    except:
        return Response(status=status.HTTP_204_NO_CONTENT)

