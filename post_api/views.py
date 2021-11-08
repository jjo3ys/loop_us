from django.shortcuts import render

from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework import status
import json

from .serializers import PostingContentsSerializer, PostingSerializer

from .models import Posting, PostingContents


# Create your views here.

@api_view(['POST', ])
@permission_classes((IsAuthenticated,))
def posting_list_load(request, proj_idx):
    if request.method == 'GET':
        try:
            postings = Posting.objects.filter(project=proj_idx)    
        except Posting.DoesNotExist:
            return Response('The postings aren\'t valid', status=status.HTTP_404_NOT_FOUND)

        postingSZ = PostingSerializer(postings, many=True)

        return_dict = {
            'posting_list' : postingSZ.data
        }
        return Response(return_dict)
    else:
        return Response('Request isn\'t valid.', status=status.HTTP_404_NOT_FOUND)

@api_view(['POST', ])
@permission_classes((IsAuthenticated,))
def specific_posting_load(request, posting_idx):
    if request.method == 'GET':
        try:
            posting = Posting.objects.get(posting=posting_idx)

        except Posting.DoesNotExist:
            return Response('The posting isn\'t valid', status=status.HTTP_404_NOT_FOUND)

        try:
            postingContents = 'default'
            postingContents = PostingContents.objects.filter(posting=posting_idx)
        
            if postingContents == 'default':
                return Response('Empty posting')
                

        except PostingContents.DoesNotExist:
            return Response('Contents aren\'t valid.', status=status.HTTP_404_NOT_FOUND)
    
    
        postingSZ = PostingSerializer(posting)
        PostingContSZ = PostingContentsSerializer(postingContents, many=True)

        return_dict = {
            'posting_info': postingSZ.data,
            'posting_content_info': PostingContSZ.data,
        }

        return Response(return_dict)

    else:
        return Response('Request isn\'t valid.', status=status.HTTP_404_NOT_FOUND)

##############################################################################################################

@api_view(['POST', ])
@permission_classes((IsAuthenticated,))
def specific_posting_update(request, user_idx, proj_idx, posting_idx):
    if str(request.user.id) == user_idx:
        postingcont = PostingContents.objects.filter(author_id=user_idx)
        postingcont.delete()
#####################################################################################
        try:
            ContentsList = json.JSONDecoder().decode(request.data['posting_list'])
            return_list = []
            i = 0
            for content in ContentsList:
#############################################################################################################################
                if content['type'] == 'title' or content['type'] == 'content':
                    customizing_model = Customizing(author=str(request.user.id))
                    customizing_sz = CustomizingSerializer(customizing_model, data={
                        'type': content['type'],
                        'contents': content['contents'],
                        'seq_id': content['id']
                })
                    if customizing_sz.is_valid():
                        customizing_sz.save()

                    else:
                        return Response('유효하지 않은 형식입니다.', status=status.HTTP_403_FORBIDDEN)

                    return_list.append(
                        {
                            "id": customizing_sz.data['seq_id'],
                            "type": customizing_sz.data['type'],
                            "contents": customizing_sz.data['contents'],
                        }
                    )

#############################################################################################################################
                elif content['type'] == 'imageURL':
                    customizing_model = Customizing(author=request.user)
                    customizing_sz = CustomizingSerializer(customizing_model, data={
                        'type': content['type'],
                        'contents': content['contents'],
                        'seq_id': content['id']
                })
                    if customizing_sz.is_valid():
                        customizing_sz.save()
                    else:
                        return Response('유효하지 않은 형식입니다.', status=status.HTTP_403_FORBIDDEN)

                    try:
                        return_list.append(
                            {
                                "id": customizing_sz.data['seq_id'],
                                "type": customizing_sz.data['type'],
                                "contents": customizing_sz.data['contents'],
                            }
                        )

                    except:
                        return Response('Error', status=status.HTTP_403_FORBIDDEN)
        except PostingContents.DoesNotExist:
            return Response('Contents aren\'t valid.', status=status.HTTP_404_NOT_FOUND)
#############################################################################################################################
                elif line['type'] == 'imageFILE':
                    customizing_model = Customizing(author=request.user)
                    customizing_sz = CustomizingSerializer(customizing_model, data={
                        'type': line['type'],
                        'contents': line['contents'],
                        'seq_id': line['id']
                })
                    if customizing_sz.is_valid():
                        customizing_sz.save()
                    else:
                        return Response('유효하지 않은 형식입니다.', status=status.HTTP_403_FORBIDDEN)

                    req_image_data = request.FILES.getlist('image')[i]
                    i = i + 1
                    try:
                        custom_model = Customizing_imgs(author=request.user)
                    except:
                        return Response('없는 사용자입니다.', status=status.HTTP_404_NOT_FOUND)
                    customizing_imgs_sz = Customizing_imgs_Serializer(
                        custom_model, data={'customizing': customizing_sz.data['id'], 'image': req_image_data})
                    try:
                        if customizing_imgs_sz.is_valid():
                            customizing_imgs_sz.save()
                        else:
                            print("데이터가 저장되지 않았습니다.")
                        return_list.append(
                            {
                                "id": customizing_sz.data['seq_id'],
                                "type": customizing_sz.data['type'],
                                "contents": customizing_imgs_sz.data['image'],
                            }
                        )
                    except:
                        return Response('유효하지 않은 image 형식입니다.??', status=status.HTTP_403_FORBIDDEN)
#####################################################################################
        try:
            posting = Posting.objects.get(posting=posting_idx)
            postingContents = PostingContents.objects.filter(posting=posting_idx)
            postingSZ = PostingSerializer(posting, data = {
                'project': request.data['project'],
                'sequance': request.data['sequance'],
                'thumbnail': request.data['thumbnail'],
                'class_num': request.data['title']
            })
            postingSZ.is_valid()
            postingSZ.save()

            postingContents_sz = PostingContentsSerializer(postingContents, data = {
                'posting_sequence': request.data['postingSeq'],
                'thumbnail': request.data['thumbnail'],
                'class_num': request.data['title']
            })
            postingContents_sz.is_valid()
            postingContents_sz.save()
            
            print('Update Completed')

            return_dict = {
                'posting': postingSZ.data,
                'posting_contents': postingContents_sz.data
            }

            return Response(return_dict)
        except:
            return Response('Request is not valid.', status=status.HTTP_404_NOT_FOUND)
    else:
        return_dict = {
            'message': ['No authority to modify.']
        }
        return Response(return_dict, status=status.HTTP_401_UNAUTHORIZED)