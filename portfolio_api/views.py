from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework import status
from rest_framework.response import Response

from portfolio_api.models import Element, Portfolio
from portfolio_api.serializers import ElementSerializers, PortfolioElementSerializers, PortfolioSerializers, SelectImageSerializers
from post_api.models import ContentsImage, Post

@api_view(['POST', 'PUT', 'GET', 'DELETE'])
@permission_classes((IsAuthenticated,))
def portfolio(request):
    if request.method == 'POST': 
        portfoilo_obj = Portfolio.objects.create(user_id = request.user.id,
                                                 introduction = request.data['introduction']) 
        return Response(PortfolioSerializers(portfoilo_obj).data, status=status.HTTP_201_CREATED)

    elif request.method == 'PUT':
        portfoilo_obj = Portfolio.objects.get(user_id=request.GET['id'])
        portfoilo_obj.introduction = request.data['introduction']
        portfoilo_obj.save()
        return Response(PortfolioSerializers(portfoilo_obj).data, status=status.HTTP_200_OK)
    
    elif request.method == 'GET': 
        try:
            portfoilo_obj = Portfolio.objects.get(user_id = request.GET['id'])
        except Portfolio.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)
        
        portfoilo = PortfolioElementSerializers(portfoilo_obj).data
        if request.user.id == portfoilo_obj.user_id:
            portfoilo.update({"is_user":1})
        else:
            portfoilo.update({"is_user":0})
        return Response(portfoilo, status=status.HTTP_200_OK)
    
    elif request.method == 'DELETE':
        portfoilo_obj = Portfolio.objects.get(user_id=request.GET['id'])
        portfoilo_obj.delete()
        return Response(status=status.HTTP_200_OK)

@api_view(['POST', 'PUT', 'DELETE'])
@permission_classes((IsAuthenticated,))
def element(request):
    if request.method == 'POST':   
        element_obj = Element.objects.create(portfolio_id = Portfolio.objects.get(user_id=request.user.id).id,
                                        image = request.FILES.get('image'),
                                        title=request.data['title']) 
        contents = []
        for d in eval(request.data['contents']):
            contents.append(d)

        element_obj.contents = str(contents)
        element_obj.save()
        return Response(ElementSerializers(element_obj).data, status=status.HTTP_201_CREATED)
    
    elif request.method == 'PUT':
        element_obj = Element.objects.get(id=request.GET['id'])
        if request.GET['type'] == 'title':
            element_obj.title = request.data['title']

        elif request.GET['type'] == 'contents':
            contents = []
            for content in eval(request.data['contents']):
                contents.append(content)
            element_obj.contents = str(contents)

        elif request.GET['type'] == 'image':
            element_obj.image.delete(save=False)
            element_obj.image = request.FILES.get('image')

        element_obj.save()
        return Response('Update OK', status=status.HTTP_200_OK)
    
    elif request.method == 'DELETE':
        element_obj = Element.objects.get(id=request.GET['id'])
        element_obj.image.delete(save=False)
        element_obj.delete()

        return Response(status=status.HTTP_200_OK)

@api_view(['GET',])
@permission_classes((IsAuthenticated,))
def select_image(request):
    post_list = Post.objects.filter(user_id=request.user.id) 
    image_list = []

    for post in post_list:
        image_objs = ContentsImage.objects.filter(post_id=post.id)
        for image in image_objs:
            image_list.append(image)
    
    return Response(SelectImageSerializers(image_list, many=True).data, status=status.HTTP_200_OK)


    

    
