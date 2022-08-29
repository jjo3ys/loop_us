from django.core.paginator import Paginator

from rest_framework import status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import api_view, permission_classes

from scout_api.models import Contact
from scout_api.serializers import ContactSerializers

from user_api.models import Profile

# Create your views here.
@api_view(['POST', 'GET'])
@permission_classes((IsAuthenticated,))
def scout_contact(request):

    type = request.GET['type']

    try:
        if type == 'all':
            contact_obj = Contact.objects.all().order_by('date')
        else:
            contact_obj = Contact.objects.filter(group_id = type).order_by('date')
    
        contact_obj = Paginator(contact_obj, 10)

        if contact_obj.num_pages < int(request.GET['page']):
            return Response(status=status.HTTP_204_NO_CONTENT)

        return Response(ContactSerializers(contact_obj.get_page(request.GET['page']), many=True).data, status=status.HTTP_200_OK)
        
    except:
        return Response(status=status.HTTP_204_NO_CONTENT)

