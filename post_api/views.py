from django.shortcuts import render

from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework import status

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

            return Response(profile_sz.data)
        except Profile.DoesNotExist:
            return Response('Request is not valid.', status=status.HTTP_404_NOT_FOUND)
    else:
        return_dict = {
            'message': ['No authority to modify.']
        }
        return Response(return_dict, status=status.HTTP_401_UNAUTHORIZED)