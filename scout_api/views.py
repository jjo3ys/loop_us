from django.core.paginator import Paginator

from rest_framework import status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import api_view, permission_classes
from loop.models import Loopship

from scout_api.models import Contact
from scout_api.serializers import CompanyProfileSerializer

from user_api.models import Company, Company_Inform, Profile

# Create your views here.
# 상단에 있는 기업 추천 이거를
# @api_view(['GET'])
# @permission_classes((IsAuthenticated,))
# def recommendation_company(request, idx):

@api_view(['GET'])
@permission_classes((IsAuthenticated,))
def recommendation_company(request):
    return Response(CompanyProfileSerializer(Company_Inform.objects.filter(group = request.GET['type'][:5]), many = True).data, status=status.HTTP_200_OK)


@api_view(['GET'])
@permission_classes((IsAuthenticated,))
def company_group(request):
    try:
        if request.GET['type'] == 'all':
            company_obj = Company_Inform.objects.all().order_by('-id')

        else:
            company_obj = Company_Inform.objects.filter(group = request.GET['type']).order_by('-id')

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

@api_view(['GET'])
@permission_classes((IsAuthenticated,))
def search_company(request):
    type = request.GET['type']

    c_obj = Company.objects.filter(company_name = request.GET['name'])
    
    if type == 'all':
        profile_obj = Company_Inform.objects.filter(company__in = c_obj)
        # 이제 기업 이름을 검색할 때 Company에서 불러오고 또 거기서 기업 프로필을 받아오는 과정에서 그럼 8만개의 데이터들에 대해서는 기업 프로필이 아직 없습니다..
